`timescale 1ns / 1ps
`default_nettype none
module demod64 #(
   parameter integer C_S00_AXIS_TDATA_WIDTH = 32,
   parameter integer C_M00_AXIS_TDATA_WIDTH = 64
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

logic [31:0] val_reg;
logic [63:0] alpha;

// todo: wire up oliver's cordic to the input
logic signed [31:0] ac;
logic signed [31:0] bd;

logic signed [31:0] bc;
logic signed [31:0] ad;

logic signed [15:0] cur_real; //a
logic signed [15:0] prev_real; //c

logic signed [15:0] cur_imag; //b
logic signed [15:0] prev_imag; //d

logic signed [31:0] final_real;
logic signed [31:0] final_imag;

always_comb begin
        s00_axis_tready = m00_axis_tready || ~m00_axis_tvalid;

        cur_real =  s00_axis_tdata[15:0];
        cur_imag =  s00_axis_tdata[31:16];

        prev_real =  val_reg[15:0];
        prev_imag =  val_reg[31:16];

        ac = ($signed(cur_real) * $signed(prev_real)) >>> 3; //
        bd = ($signed(cur_imag) * $signed(prev_imag)) >>> 3;

        bc = ($signed(cur_imag) * $signed(prev_real)) >>> 3;
        ad = ($signed(cur_real) * $signed(prev_imag)) >>> 3;

        final_real  = $signed(ac + bd);
        final_imag  = $signed(bc - ad);

        alpha = {final_imag,final_real};
       //alpha = {16'b0,cur_imag,16'b0,cur_real};
       //alpha = {32'hDEADDEAD,32'hBEEFBEEF};
end

always_ff @(posedge s00_axis_aclk)begin
   if(!s00_axis_aresetn)begin
       // don't do anything
       m00_axis_tvalid <= 0;
       val_reg <= 0;
       m00_axis_tdata <= 0;
       m00_axis_tstrb <= 0;
       m00_axis_tlast <= 0;
   end else begin
       if(s00_axis_tvalid && s00_axis_tready)begin
           // grab valid data and compute the difference
           val_reg <= s00_axis_tdata;
           m00_axis_tdata <= alpha;
           m00_axis_tvalid <= 1'b1;
           m00_axis_tlast <= s00_axis_tlast;
           m00_axis_tstrb <= 255;
       end else begin
           m00_axis_tvalid <= 1'b0;
       end
   end
end

endmodule
