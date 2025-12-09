module demod_w#(C_S00_AXIS_TDATA_WIDTH=32, C_M00_AXIS_TDATA_WIDTH=64)(
   input wire s00_axis_aclk,
   input wire s00_axis_aresetn,
   input wire s00_axis_tlast,
   input wire s00_axis_tvalid,
   input wire [C_S00_AXIS_TDATA_WIDTH-1:0] s00_axis_tdata,
   input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] s00_axis_tstrb,
   output wire s00_axis_tready,

   input wire m00_axis_aclk,
   input wire m00_axis_tready,
   output wire m00_axis_tvalid,
   output wire m00_axis_tlast,
   output wire [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
   output wire [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb
);


	demod64 demody(
	   .s00_axis_aclk(s00_axis_aclk),
	   .s00_axis_aresetn(s00_axis_aresetn),
	   .s00_axis_tlast(s00_axis_tlast),
	   .s00_axis_tvalid(s00_axis_tvalid),
	   .s00_axis_tdata(s00_axis_tdata),
	   .s00_axis_tstrb(s00_axis_tstrb),
	   .s00_axis_tready(s00_axis_tready),
	   .m00_axis_tready(m00_axis_tready),
	   .m00_axis_tvalid(m00_axis_tvalid),
	   .m00_axis_tlast(m00_axis_tlast),
	   .m00_axis_tdata(m00_axis_tdata), // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
	   .m00_axis_tstrb(m00_axis_tstrb)
	);



endmodule
