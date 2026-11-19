module AGX_5E_065B_Modular_DevKit_HSB_MIPI_10GbE_qsys_test_counter_0 #(
		parameter DATA_WIDTH = 64
	) (
		input  wire                                  clk,           //             clock.clk
		input  wire                                  reset_n,       //             reset.reset_n
		output wire                                  m_axis_tvalid, // axi4stream_master.tvalid
		input  wire                                  m_axis_tready, //                  .tready
		output wire [(((DATA_WIDTH-1)-0)+1)-1:0]     m_axis_tdata,  //                  .tdata
		output wire                                  m_axis_tlast,  //                  .tlast
		output wire [((((DATA_WIDTH/8)-1)-0)+1)-1:0] m_axis_tkeep,  //                  .tkeep
		output wire [1:0]                            m_axis_tuser   //                  .tuser
	);
endmodule

