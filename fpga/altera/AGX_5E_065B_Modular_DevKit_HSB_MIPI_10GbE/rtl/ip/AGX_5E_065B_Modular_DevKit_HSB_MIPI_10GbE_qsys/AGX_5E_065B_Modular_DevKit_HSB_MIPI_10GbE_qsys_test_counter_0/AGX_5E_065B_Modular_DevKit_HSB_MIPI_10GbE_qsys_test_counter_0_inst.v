	AGX_5E_065B_Modular_DevKit_HSB_MIPI_10GbE_qsys_test_counter_0 #(
		.DATA_WIDTH (INTEGER_VALUE_FOR_DATA_WIDTH)
	) u0 (
		.clk           (_connected_to_clk_),           //   input,                           width = 1,             clock.clk
		.reset_n       (_connected_to_reset_n_),       //   input,                           width = 1,             reset.reset_n
		.m_axis_tvalid (_connected_to_m_axis_tvalid_), //  output,                           width = 1, axi4stream_master.tvalid
		.m_axis_tready (_connected_to_m_axis_tready_), //   input,                           width = 1,                  .tready
		.m_axis_tdata  (_connected_to_m_axis_tdata_),  //  output,      width = (((DATA_WIDTH-1)-0)+1),                  .tdata
		.m_axis_tlast  (_connected_to_m_axis_tlast_),  //  output,                           width = 1,                  .tlast
		.m_axis_tkeep  (_connected_to_m_axis_tkeep_),  //  output,  width = ((((DATA_WIDTH/8)-1)-0)+1),                  .tkeep
		.m_axis_tuser  (_connected_to_m_axis_tuser_)   //  output,                           width = 2,                  .tuser
	);

