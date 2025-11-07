`timescale 1ns / 1ps
`default_nettype none
module demodulate (
    // Ports of Axi Slave Bus Interface S00_AXIS
    input wire s00_axis_aclk,
    input wire s00_axis_aresetn,
    input wire s00_axis_tlast,
    input wire s00_axis_tvalid,
    input wire [C_S00_AXIS_TDATA_WIDTH-1:0] s00_axis_tdata,
    input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1:0] s00_axis_tstrb,
    output logic s00_axis_tready,

    // Ports of Axi Master Bus Interface M00_AXIS
    input wire m00_axis_tready,
    output logic m00_axis_tvalid,
    output logic m00_axis_tlast,
    output logic [C_M00_AXIS_TDATA_WIDTH-1:0] m00_axis_tdata, // [15:0] is magnitude (unsigned 16-bit integer). [31:16] is angle.
    output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1:0] m00_axis_tstrb
);
    // inputs :
    // iq data from anothe module i think iq framer???
    // where are the i and the q values going to be coming from???

    // outputs : 
    // demodulated signal in some bits??

    // I think I am going to need to orchestrate these signals better to make it axi compliant

    number_cruncher cordic(
        .s00_axis_aclk(s00_axis_aclk),
        .s00_axis_aresetn(),
        .s00_axis_tlast(),
        .s00_axis_tvalid(),
        .s00_axis_tdata(),
        .s00_axis_tstrb(),
        .s00_axis_tready(),
        .m00_axis_tready(),
        .m00_axis_tvalid(),
        .m00_axis_tlast(),
        .m00_axis_tdata(),
        .m00_axis_tstrb()
    );

    if(m00_axis_tready && something???)begin
        final_res <= res >> 1; // step 1 cordic signal // step 2 multiply by 1/2 // step 3 profit????
    end


endmodule


`default_nettype wire
