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

    output logic [C_M00_AXIS_TDATA_WIDTH-1:0] snooped_data,
    output logic snooped_valid,
);

    // this module can consume the same data from cordic but it cannot put back pressure
    always_comb begin
        // check for valid handshake
        
    end

endmodule

`default_nettype wire
