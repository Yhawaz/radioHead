`timescale 1ns / 1ps
`default_nettype none
module fir_19_wrap #(
   parameter integer C_S00_AXIS_TDATA_WIDTH = 64,
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
   output logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, 
   output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb
);


always_comb begin
        s00_axis_tready = m00_axis_tready;// || ~m00_axis_tvalid;
        m00_axis_tstrb = 255; // rewrite to respect valid handshake and test that it respects back pressure
end

always_ff @(posedge s00_axis_aclk)begin
   if(!s00_axis_aresetn)begin
       // don't do anything
       m00_axis_tvalid <= 0;
       val_reg <= 0;
       m00_axis_tdata <= 0;
       //m00_axis_tstrb <= 0;
       m00_axis_tlast <= 0;
   end else begin
       if(s00_axis_tvalid && s00_axis_tready)begin
           // grab valid data and compute the difference
           val_reg <= s00_axis_tdata;
           m00_axis_tdata <= ;
           m00_axis_tvalid <= 1'b1;
           m00_axis_tlast <= s00_axis_tlast;
           //m00_axis_tstrb <= 255;
       end else begin
            m00_axis_tvalid <= 1'b0;

       end
   end
end

Filter filty(
    .clk(s00_axis_clk_in),
    .reset(s00_axis_aresetn),
    .enb(1'b1),
    .dataIn(s00_axis_tvalid),
    .validIn(s00_axis_tdata),
    .syncReset(),
    .dataOut(m00_axis_tdata),
    .validOut(m00_axis_tvalid));

endmodule

