module AXI_monitor_w#(C_M00_AXIS_TDATA_WIDTH = 64)(

    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,

    // Ports of Axi Master Bus Interface M00_AXIS
    input wire m00_axis_tready,
    input wire m00_axis_tvalid,
    input wire [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.

    output wire [C_M00_AXIS_TDATA_WIDTH/2-1:0] snooped_tdata
);


	AXI_monitor watcher(
	   .s00_axis_aclk(s00_axis_aclk),
	   .s00_axis_aresetn(s00_axis_aresetn),
	   .m00_axis_tready(m00_axis_tready),
	   .m00_axis_tvalid(m00_axis_tvalid),
	   .m00_axis_tdata(m00_axis_tdata), // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
	   .snooped_tdata(snooped_tdata)
	);



endmodule
