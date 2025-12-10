`timescale 1ns / 1ps
`default_nettype none
module triple_wave_maker #(
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

logic dummy_ce_1;
logic dummy_ce_2;
logic [69:0] pilot_tone_data;
logic pilot_tone_valid;

logic [63:0] triple_in_data;
logic [63:0] triple_out_data;


logic[69:0] nco_57_data;

//get pilot tone
fm32bit_19kHz_filter pilot_getter(.clk(s00_axis_aclk),
                                 .reset(!s00_axis_aresetn),
                                .clk_enable(1'b1),
                                .dataIn(s00_axis_tdata),
                                .validIn(s00_axis_tvalid),
                                .ce_out(dummy_ce_1),
                                .dataOut(pilot_tone_data),
                                .validOut(pilot_tone_valid));

triple tripler(.data_in(triple_in_data),
                .data_out(triple_out_data));

fm32bit_57kHz_filter tripled_19_at_57(.clk(s00_axis_aclk),
                                 .reset(!s00_axis_aresetn),
                                .clk_enable(1'b1),
                                .dataIn(triple_out_data),
                                .validIn(pilot_tone_valid),
                                .ce_out(dummy_ce_2),
                                .dataOut(nco_57_data),
                                .validOut(m00_axis_tvalid));

always_comb begin
        s00_axis_tready = m00_axis_tready;// || ~m00_axis_tvalid;
        m00_axis_tstrb = 255; // rewrite to respect valid handshake and test that it respects back pressure
        triple_in_data = $signed(pilot_tone_data) >>> 37;
        m00_axis_tdata = $signed(nco_57_data) >>> 37;
end

endmodule

`default_nettype wire
