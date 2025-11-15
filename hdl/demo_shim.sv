`timescale 1ns / 1ps
`default_nettype none
module demo_shim #(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 32,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 32
)(
    // ports of axi slave bus interface s00_axis
    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,
    input wire s00_axis_tlast,
    input wire s00_axis_tvalid,
    input wire [C_S00_AXIS_TDATA_WIDTH-1:0] s00_axis_tdata,
    input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] s00_axis_tstrb,
    output logic s00_axis_tready,

    // ports of axi master bus interface m00_axis
    input wire m00_axis_tready,
    output logic m00_axis_tvalid,
    output logic m00_axis_tlast,
    output logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
    output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb
);

	logic meow_ready;
	logic meow_valid;
	logic meow_last;
	logic [C_M00_AXIS_TDATA_WIDTH-1:0] meow_data; 
	logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] meow_strb;

	cordic angle_maker(
		.s00_axis_aclk(s00_axis_aclk),
		.s00_axis_aresetn(s00_axis_aresetn),
		.s00_axis_tlast(s00_axis_tlast),
		.s00_axis_tvalid(s00_axis_tvalid),
		.s00_axis_tdata(s00_axis_tdata),
		.s00_axis_tstrb(s00_axis_tstrb),
		.s00_axis_tready(s00_axis_tready),

		.m00_axis_tready(meow_ready),
		.m00_axis_tvalid(meow_valid),
		.m00_axis_tlast(meow_last),
		.m00_axis_tdata(meow_data),
		.m00_axis_tstrb(meow_strb)
	);

	demodulate dmoder(
		.s00_axis_aclk(s00_axis_aclk),
		.s00_axis_aresetn(s00_axis_aresetn),
		.s00_axis_tlast(meow_last),
		.s00_axis_tvalid(meow_valid),
		.s00_axis_tdata(meow_data),
		.s00_axis_tstrb(meow_strb),
		.s00_axis_tready(meow_ready),

		.m00_axis_tready(m00_axis_tready),
		.m00_axis_tvalid(m00_axis_tvalid),
		.m00_axis_tlast(m00_axis_tlast),
		.m00_axis_tdata(m00_axis_tdata),
		.m00_axis_tstrb(m00_axis_tstrb)
	);

endmodule


`default_nettype wire


