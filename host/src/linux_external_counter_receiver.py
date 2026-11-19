import argparse
import logging

import numpy as np
import cupy as cp

import cuda.bindings.driver as cuda
import holoscan
import hololink as hololink_module

"""class CounterGenerator:
    def __init__(self, hololink, sif_index, frame_size):
        self.hololink = hololink
        self.sif_index = sif_index
        self.frame_size = frame_size

        # HSB SIF RX data-generator register base
        self.base = 0x01000100 + (0x10000 * sif_index)

    def start(self):
        logging.info("Enabling counter generator on SIF %d", self.sif_index)

        # Disable generator before configuring it
        self.hololink.write_uint32(self.base + 0x04, 0x00000000)

        # Counter mode
        self.hololink.write_uint32(self.base + 0x08, 0x00000001)

        # Frame size, in bytes
        self.hololink.write_uint32(self.base + 0x0C, self.frame_size)

        # Output rate
        self.hololink.write_uint32(self.base + 0x10, 0x00007FFF)

        # Enable one-shot generation (continuous bit = 0)
        self.hololink.write_uint32(self.base + 0x04, 0x00000001)

    def stop(self):
        logging.info("Disabling counter generator")
        self.hololink.write_uint32(self.base + 0x04, 0x00000000)"""

class CounterGenerator:
    def start(self):
        print("Starting FPGA counter")

        # Later: send a start command to the FPGA

    def stop(self):
        print("Stopping FPGA counter")

        # Later: send a stop command to the FPGA

import numpy as np
import cupy as cp


class CounterDumpOperator(holoscan.core.Operator):

    def __init__(self, fragment, frame_size, *args, **kwargs):
        self.frame_size = frame_size
        self.frame_count = 0
        super().__init__(fragment, *args, **kwargs)

    def setup(self, spec):
        spec.input("input")

    def compute(self, op_input, op_output, context):

        message = op_input.receive("input")

        if message is None:
            return

        # C++ Holoscan operators can deliver a TensorMap,
        # represented as a dictionary in the Python operator.
        if isinstance(message, dict):
            candidates = [
                value for value in message.values()
                if hasattr(value, "__cuda_array_interface__")
                or hasattr(value, "__array_interface__")
            ]

            if not candidates:
                raise RuntimeError(
                    f"No tensor found in receiver output: {message.keys()}"
                )

            tensor = candidates[0]
        else:
            tensor = message

        # Access GPU memory and copy the data to CPU memory
        gpu_array = cp.asarray(tensor)
        host_array = cp.asnumpy(gpu_array)

        # Interpret received data as a byte stream
        raw = np.ascontiguousarray(host_array).view(np.uint8).reshape(-1)

        # Generator uses 16-bit counter values
        words = raw[:self.frame_size].view("<u8")

        self.frame_count += 1
        print(f"Frame")

        print(f"\nReceived frame: {self.frame_count}")
        print(f"Frame bytes: {raw.size}")
        print(f"First 16 counter values: {words[:512].tolist()}")

        # Check sequential counter values
        if len(words) > 1:
            differences = (
                words[1:].astype(np.uint32)
                - words[:-1].astype(np.uint32)
            ) & 0xFFFF

            sequential = np.all(differences == 1)
            print(f"Sequential counter: {sequential}")

class CounterApplication(holoscan.core.Application):

    def __init__(
        self,
        cuda_context,
        hololink_channel,
        generator,
        frame_size,
        frame_limit=1,
    ):
        super().__init__()

        self.cuda_context = cuda_context
        self.hololink_channel = hololink_channel
        self.generator = generator
        self.frame_size = frame_size
        self.frame_limit = frame_limit

    def compose(self):

        condition = holoscan.conditions.CountCondition(
            self,
            name="count",
            count=self.frame_limit,
        )

        # Standard Linux socket receiver.
        # No ConnectX/RDMA hardware is needed.
        receiver = hololink_module.operators.LinuxReceiverOperator(
            self,
            condition,
            name="receiver",
            frame_size=self.frame_size,
            frame_context=self.cuda_context,
            hololink_channel=self.hololink_channel,
            device=self.generator,
        )

        # Read and print received counter data
        counter_dump = CounterDumpOperator(
            self,
            name="counter_dump",
            frame_size=self.frame_size,
        )

        self.add_flow(
            receiver,
            counter_dump,
            {("output", "input")},
        )

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--hololink",
        default="192.168.0.2",
    )

    parser.add_argument(
        "--sensor",
        type=int,
        default=0,
        choices=(0, 1),
    )

    parser.add_argument(
        "--sif-index",
        type=int,
        default=0,
        choices=(0, 1, 2),
    )

    parser.add_argument(
        "--frame-size",
        type=int,
        default=4096,
    )

    args = parser.parse_args()

    if args.frame_size <= 0 or args.frame_size % 8:
        parser.error("--frame-size must be positive and divisible by 8")

    # Initialize CUDA
    (result,) = cuda.cuInit(0)
    assert result == cuda.CUresult.CUDA_SUCCESS

    cu_device_ordinal = 0

    result, cu_device = cuda.cuDeviceGet(cu_device_ordinal)
    assert result == cuda.CUresult.CUDA_SUCCESS

    result, cu_context = cuda.cuDevicePrimaryCtxRetain(cu_device)
    assert result == cuda.CUresult.CUDA_SUCCESS

    # Agilex 5 board enumeration configuration
    b_mdk_uuid = "7b1fa8c7-31aa-44b6-abcc-eac134461fdc"
    a_mdk_uuid = "b26763ac-af25-44f6-850e-dce30f33f4e3"

    uuid_strategy = hololink_module.BasicEnumerationStrategy(
        total_sensors=2,
        total_dataplanes=1,
        sifs_per_sensor=1,
    )

    hololink_module.Enumerator.set_uuid_strategy(
        a_mdk_uuid, uuid_strategy
    )
    hololink_module.Enumerator.set_uuid_strategy(
        b_mdk_uuid, uuid_strategy
    )

    # Discover HSB
    channel_metadata = hololink_module.Enumerator.find_channel(
        channel_ip=args.hololink
    )

    metadata = hololink_module.Metadata(channel_metadata)

    metadata.update(
        hololink_module.Metadata({
            "vsync_enable": 0,
            "ptp_enable": 0,
        })
    )

    # Select logical sensor/data channel
    hololink_module.DataChannel.use_sensor(
        metadata, args.sensor
    )

    hololink_channel = hololink_module.DataChannel(metadata)

    hololink = hololink_channel.hololink()

    # Create internal FPGA generator controller
    """generator = CounterGenerator(
        hololink,
        args.sif_index,
        args.frame_size,
    )"""
    generator = CounterGenerator()

    # Create receiver app
    application = CounterApplication(
        cu_context,
        hololink_channel,
        generator,
        args.frame_size,
        frame_limit=10000,
    )

    hololink.start()

    try:
        hololink.reset()

        logging.info("Starting counter receiver")
        application.run()

    finally:
        generator.stop()
        hololink.stop()

    (result,) = cuda.cuDevicePrimaryCtxRelease(cu_device)
    assert result == cuda.CUresult.CUDA_SUCCESS


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()