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

	logic demod_to_cordic_ready;
	logic demod_to_cordic_valid;
	logic demod_to_cordic_last;
	logic [63:0] demod_to_cordic_data; 
	logic [63:0] demod_to_cordic_data_shifted; 
	logic [7:0] demod_to_cordic_strb;

    always_comb begin
       demod_to_cordic_data_shifted = {demod_to_cordic_data[63:32]<<8,demod_to_cordic_data[31:0]<<8}; 
    end

	demod64 demod(
		.s00_axis_aclk(s00_axis_aclk),
		.s00_axis_aresetn(s00_axis_aresetn),
		.s00_axis_tlast(s00_axis_tlast),
		.s00_axis_tvalid(s00_axis_tvalid),
		.s00_axis_tdata(s00_axis_tdata),
		.s00_axis_tstrb(s00_axis_tstrb),
		.s00_axis_tready(s00_axis_tready),

		.m00_axis_tready(demod_to_cordic_ready),
		.m00_axis_tvalid(demod_to_cordic_valid),
		.m00_axis_tlast(demod_to_cordic_last),
		.m00_axis_tdata(demod_to_cordic_data),
		.m00_axis_tstrb(demod_to_cordic_strb)
	);

	cordic angle_time(
		.s00_axis_aclk(s00_axis_aclk),
		.s00_axis_aresetn(s00_axis_aresetn),
		.s00_axis_tlast(demod_to_cordic_last),
		.s00_axis_tvalid(demod_to_cordic_valid),
		.s00_axis_tdata({demod_to_cordic_data_shifted[63:48],demod_to_cordic_data_shifted[31:16]}),
		.s00_axis_tstrb(demod_to_cordic_strb[3:0]),
		.s00_axis_tready(demod_to_cordic_ready),

		.m00_axis_tready(m00_axis_tready),
		.m00_axis_tvalid(m00_axis_tvalid),
		.m00_axis_tlast(m00_axis_tlast),
		.m00_axis_tdata(m00_axis_tdata),
		.m00_axis_tstrb(m00_axis_tstrb)
	);

endmodule


`default_nettype wire


