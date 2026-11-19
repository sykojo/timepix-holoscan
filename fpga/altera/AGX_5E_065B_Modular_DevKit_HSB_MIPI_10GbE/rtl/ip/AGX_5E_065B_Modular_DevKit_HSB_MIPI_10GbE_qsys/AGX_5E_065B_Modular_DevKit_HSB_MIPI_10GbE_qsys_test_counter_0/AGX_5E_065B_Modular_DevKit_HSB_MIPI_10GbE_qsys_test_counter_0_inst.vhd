	component AGX_5E_065B_Modular_DevKit_HSB_MIPI_10GbE_qsys_test_counter_0 is
		generic (
			DATA_WIDTH : integer := 64
		);
		port (
			clk           : in  std_logic                                               := 'X'; -- clk
			reset_n       : in  std_logic                                               := 'X'; -- reset_n
			m_axis_tvalid : out std_logic;                                                      -- tvalid
			m_axis_tready : in  std_logic                                               := 'X'; -- tready
			m_axis_tdata  : out std_logic_vector((((DATA_WIDTH-1)-0)+1)-1 downto 0);            -- tdata
			m_axis_tlast  : out std_logic;                                                      -- tlast
			m_axis_tkeep  : out std_logic_vector(((((DATA_WIDTH/8)-1)-0)+1)-1 downto 0);        -- tkeep
			m_axis_tuser  : out std_logic_vector(1 downto 0)                                    -- tuser
		);
	end component AGX_5E_065B_Modular_DevKit_HSB_MIPI_10GbE_qsys_test_counter_0;

	u0 : component AGX_5E_065B_Modular_DevKit_HSB_MIPI_10GbE_qsys_test_counter_0
		generic map (
			DATA_WIDTH => INTEGER_VALUE_FOR_DATA_WIDTH
		)
		port map (
			clk           => CONNECTED_TO_clk,           --             clock.clk
			reset_n       => CONNECTED_TO_reset_n,       --             reset.reset_n
			m_axis_tvalid => CONNECTED_TO_m_axis_tvalid, -- axi4stream_master.tvalid
			m_axis_tready => CONNECTED_TO_m_axis_tready, --                  .tready
			m_axis_tdata  => CONNECTED_TO_m_axis_tdata,  --                  .tdata
			m_axis_tlast  => CONNECTED_TO_m_axis_tlast,  --                  .tlast
			m_axis_tkeep  => CONNECTED_TO_m_axis_tkeep,  --                  .tkeep
			m_axis_tuser  => CONNECTED_TO_m_axis_tuser   --                  .tuser
		);

