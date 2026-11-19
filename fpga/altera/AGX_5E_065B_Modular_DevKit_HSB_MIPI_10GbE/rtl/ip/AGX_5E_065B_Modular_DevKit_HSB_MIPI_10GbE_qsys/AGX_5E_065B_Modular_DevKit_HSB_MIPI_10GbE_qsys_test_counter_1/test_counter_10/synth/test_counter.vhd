library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity simple_hsb_source is
    generic (
        DATA_WIDTH : integer := 32
    );
    port (
        clk           : in  std_logic;
        reset_n       : in  std_logic;
        
        -- AXI4-Stream Source matching HSB requirements
        m_axis_tvalid : out std_logic;
        m_axis_tready : in  std_logic;
        m_axis_tdata  : out std_logic_vector(DATA_WIDTH-1 downto 0);
        m_axis_tlast  : out std_logic;
        m_axis_tkeep  : out std_logic_vector((DATA_WIDTH/8)-1 downto 0);
        m_axis_tuser  : out std_logic_vector(1 downto 0)
    );
end entity simple_hsb_source;

architecture rtl of simple_hsb_source is
    signal count       : unsigned(DATA_WIDTH-1 downto 0);
    signal tlast_int   : std_logic;

    -- Registered output signals
    signal r_tdata     : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal r_tlast     : std_logic;
begin

    -- Assign registered signals to ports
    m_axis_tvalid <= '1';
    m_axis_tdata  <= r_tdata;
    m_axis_tlast  <= r_tlast;
    m_axis_tkeep  <= (others => '1');
    m_axis_tuser  <= "00";

    -- Combinatorial helper for tlast condition
    tlast_int <= '1' when count = 1023 else '0';

    process(clk)
    begin
        if reset_n = '0' then
            count   <= (others => '0');
            r_tdata <= (others => '0');
            r_tlast <= '0';
         elsif rising_edge(clk) then
            -- Increment counter and update outputs only on successful handshake
            if m_axis_tready = '1' then
                if count = 1023 then
                    count <= (others => '0');
                else
                    count <= count + 1;
                end if;

                -- Update registered data and last for the next cycle
                r_tdata <= std_logic_vector(count);
                r_tlast <= tlast_int;
            end if;
        end if;
    end process;

end architecture rtl;
