`timescale 1ns / 1ps
`default_nettype none
module AXI_monitor #(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 64,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 64
)(
    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,
    // Ports of Axi Master Bus Interface M00_AXIS
    input wire m00_axis_tready,
    input logic m00_axis_tvalid,
    input logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.

    output logic [C_M00_AXIS_TDATA_WIDTH/2-1:0] snooped_tdata
);

    // this module can consume the same data from cordic but it cannot put back pressure
    logic valid_handshake;
    always_comb begin
        // check for valid handshake for intaking data from cordic
        valid_handshake = m00_axis_tready & m00_axis_tvalid;
    end

    always_ff @(posedge s00_axis_aclk)begin
		// this module will cannot accept backpressure to not interfe
		// with the upstream data stream
        // however it should only update when there is a valid transaction
        if(valid_handshake)begin
		    snooped_tdata <= m00_axis_tdata[63:32]; // grabbing the angle
        end
    end

endmodule

`default_nettype wire
