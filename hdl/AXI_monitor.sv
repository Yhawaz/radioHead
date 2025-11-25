`timescale 1ns / 1ps
`default_nettype none
module AXI_monitor #(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 32,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 32,
)(
    // Ports of Axi Slave Bus Interface S00_AXIS
    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,
    input wire s00_axis_tlast,
    input wire s00_axis_tvalid,
    input wire [C_S00_AXIS_TDATA_WIDTH-1:0] s00_axis_tdata,
    input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] s00_axis_tstrb,
    input logic s00_axis_tready,

    // Ports of Axi Master Bus Interface M00_AXIS
    input wire m00_axis_tready,
    input logic m00_axis_tvalid,
    input logic m00_axis_tlast,
    input logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
    input logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb,

    // Ports of second Axi Master Bus Interface M01_AXIS
    input wire m01_axis_tready, // this signal has to be ignored becauset this module cannot convey back pressure
    output logic m01_axis_tvalid,
    output logic m01_axis_tlast,
    output logic [C_M00_AXIS_TDATA_WIDTH-1:0] m01_axis_tdata,
    output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m01_axis_tstrb
);

    // this module can consume the same data from cordic but it cannot put back pressure
    logic valid_handshake;
    always_comb begin
        // check for valid handshake for intaking data from cordic
	m01_axis_tstrb = 4'b1111;
    end

    always_ff @(posedge s00_axis_aclk)begin
	if(s00_axis_aresetn == 1'b0)begin
		// active low reset
		snooped_data <= 0;
		snooped_valid <= 1'b1;
	end else begin
		// this module will cannot accept backpressure to not interfer
		// with the upstream data stream
		m01_axis_tvalid <= s00_axis_tvalid;
		m01_axis_tdata <= s00_axis_tdata[31:16]; // grabbing the angle
		m01_axis_tlast <= s00_axis_tlast;
	end
    end

endmodule

`default_nettype wire
