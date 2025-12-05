`timescale 1ns / 1ps
`default_nettype none
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:  Joe Steinmeyer
//
// Create Date: 09/12/2025 05:11:30 AM
// Module Name: fir_wrapper
// Project Name: week03 6.S965 Fall 2025
// Target Devices: 7000 series Zynq (7020 on Pynq Z2)
// Tool Versions: (Vivado 2025.1)
// Description:  wraps up three separate fir_15 devices (one for each color channel
// handles splitting the pixel up into channels and putting back together
// as well as having spots for offset binary conversion, shifting the outputs of the
// FIR and doing clipping (completed by student).
//
// Dependencies: fir_15 from work earlier in week.
//
// Revision:
// Revision 0.01 - File Created
//
//////////////////////////////////////////////////////////////////////////////////


module fir_wrapper#(    
        parameter integer C_S00_AXIS_TDATA_WIDTH    = 64,
        parameter integer C_M00_AXIS_TDATA_WIDTH    = 32
    )(
    input wire  s00_axis_aclk, s00_axis_aresetn,
    input wire  s00_axis_tlast, s00_axis_tvalid,

    input wire [C_S00_AXIS_TDATA_WIDTH - 1:0] s00_axis_tdata,
    input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1: 0] s00_axis_tstrb,
    output wire s00_axis_tready,

    input wire  m00_axis_aclk, m00_axis_aresetn,
    input wire  m00_axis_tready,
    output wire  m00_axis_tvalid, m00_axis_tlast,
    output wire [C_M00_AXIS_TDATA_WIDTH - 1:0] m00_axis_tdata,
    output wire [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb

    );

    wire [3:0] scaler;
    wire signed [C_M00_AXIS_TDATA_WIDTH - 1:0] fir_out;
    reg [C_M00_AXIS_TDATA_WIDTH - 1:0]  m00_axis_tdata_reg;
    reg m00_axis_tvalid_reg;
    assign scaler = 4'd12; // determined precompile

    assign m00_axis_tready = s00_axis_tready;
    assign m00_axis_tdata = $signed(fir_out >>> scaler);


    axis_fir_15 filter(     .s00_axis_aclk(s00_axis_aclk),
                .s00_axis_aresetn(s00_axis_aresetn),
                .s00_axis_tdata(s00_axis_tdata),
                .s00_axis_tstrb(s00_axis_tstrb),
                .s00_axis_tvalid(s00_axis_tvalid),
                .s00_axis_tready(s00_axis_tready),
                .m00_axis_tready(m00_axis_tready),
                .m00_axis_tdata(fir_out),
                .m00_axis_tvalid(m00_axis_tvalid),
                .m00_axis_tstrb(m00_axis_tstrb),
                .m00_axis_tlast(m00_axis_tlast)
        );
    // always @(posedge s00_axis_aclk)begin
    //     if (s00_axis_aresetn)begin
    //         m00_axis_tdata_reg <= 32'b0;
    //     end else begin
    //         //6S965 Student: CHANGED!!!
    //         m00_axis_tvalid_reg <= fir_valid;
    //     end
    // end




endmodule


`default_nettype wire


