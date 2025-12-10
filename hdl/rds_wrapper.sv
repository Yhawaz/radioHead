`timescale 1ns / 1ps
`default_nettype none
module rds_wrapper #(
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
logic [63:0] pilot_tone_data;
logic pilot_tone_valid;

logic [63:0] triple_to_filter_data;
logic triple_to_filter_valid;

logic[69:0] real_57_data;
logic[69:0] nco_57_data;

logic real_57_valid;
logic nco_57_valid

logic real_57waiting;
logic nco_57waiting;


//get pilot tone
fm32bit_19kHz_filter pilot_getter(.clk(s00_axis_aclk),
                                 .reset(s00_axis_aresetn),
                                .clk_enable(1'b1),
                                .dataIn(s00_axis_tdata),
                                .validIn(s00_axis_tvalid),
                                .ce_out(dummy_ce_1),
                                .dataOut(pilot_tone_data),
                                .validOut(pilot_tone_valid);

triple tripler(.data_in(pilot_tone_data),
                .data_out(pilot_tone_data>>3));

fm32bit_57kHz_filter tripled_19_at_57(.clk(s00_axis_aclk),
                                 .reset(s00_axis_aresetn),
                                .clk_enable(1'b1),
                                .dataIn(triple_data),
                                .validIn(pilot_tone_tvalid),
                                .ce_out(dummy_ce_2),
                                .dataOut(),
                                .validOut();

fm32bit_57kHz_filter normal_57(.clk(s00_axis_aclk),
                                 .reset(s00_axis_aresetn),
                                .clk_enable(1'b1),
                                .dataIn(s00_axis_tdata),
                                .validIn(pilot_tone_valid),
                                .ce_out(dummy_ce_2),
                                .dataOut(),
                                .validOut();


//get pilot tone tripled

//get rds

always_comb begin
        s00_axis_tready = m00_axis_tready;// || ~m00_axis_tvalid;
        m00_axis_tstrb = 255; // rewrite to respect valid handshake and test that it respects back pressure
end

always_ff @(posedge s00_axis_aclk)begin
   if(!s00_axis_aresetn)begin
       m00_axis_tvalid <= 0;
       val_reg <= 0;
       m00_axis_tdata <= 0;
       m00_axis_tlast <= 0;
   end else begin
        if(real_57_valid)begin
            if(nco_57_valid)begin
                //both valid 
                nco_57

            end else if(nco_57_waiting)begin


            end else begin

            end
        end else begin
            if(nco_57_valid)begin

                if(real_57_valid)begin

                end else if (real_57_waiting)begin


                end else begin

                end
        end else begin
            m00_axis_tdata<=0
        end

    end
end

endmodule
