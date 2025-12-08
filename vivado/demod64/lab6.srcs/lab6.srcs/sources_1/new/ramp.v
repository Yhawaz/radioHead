`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12/07/2025 01:55:24 PM
// Design Name: 
// Module Name: ramp
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module ramp(
    input wire clk,
    input wire reset,
    input wire d_valid,
    output wire [7:0] ramp_out,
    input wire btn,
    input wire [7:0] good_data
    );
    reg [7:0] ramp_out_reg;
    assign ramp_out = ramp_out_reg;
    always @(posedge clk)begin
        if(btn && d_valid)begin
             ramp_out_reg <= ramp_out_reg + 1;
        end else begin
             if(d_valid)begin
                  ramp_out_reg <= good_data;
             end
        end
   end
endmodule
