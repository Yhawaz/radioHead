`timescale 1ns / 1ps
`default_nettype none

module fir_wrapper#(    
        parameter integer NUM_COEFFS = 101,
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
    output wire [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb,
    //output wire signed [C_M00_AXIS_TDATA_WIDTH - 1:0]  pre_tdata, shifted_val,flipped_vals,

    input wire [3:0] shift
    //input wire signed [NUM_COEFFS-1:0][7:0] coeffs

    );
    //localparam NUM_COEFFS = 101;
    wire [3:0] scaler;
    reg signed [C_M00_AXIS_TDATA_WIDTH-1:0] shifted_val;
    reg [C_M00_AXIS_TDATA_WIDTH-1:0] m_tdata_reg;
    wire signed [C_M00_AXIS_TDATA_WIDTH - 1:0] fir_out;
    wire signed [C_M00_AXIS_TDATA_WIDTH - 1:0] flipped_vals;
    wire [C_M00_AXIS_TDATA_WIDTH - 1:0] pre_tdata;
    //wire [C_M00_AXIS_TDATA_WIDTH - 1:0]  pre_tdata, shifted_val,flipped_vals;
    //reg m00_axis_tvalid_reg;
    assign scaler = 4'd12; // determined precompile
    wire flipped_bit;
    wire [7:0] shft_amt;

    assign shft_amt = scaler + shift;

    // new approach
    always @(*) begin
        shifted_val = $signed(fir_out >>> shft_amt) + $signed(128);
        if(shifted_val > 255)begin
            m_tdata_reg = 255;
        end else if (shifted_val < 0) begin
            m_tdata_reg = 0;
        end else begin
            m_tdata_reg = $unsigned(shifted_val);
        end
    end



    assign m00_axis_tdata = m_tdata_reg; // dac can only take 8 bits

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
                //.coeffs(coeffs)
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



