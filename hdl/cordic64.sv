`timescale 1ns / 1ps
`default_nettype none
module cordic64 #(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 64,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 64,
    parameter integer C_NUM_CORDIC_ITERATIONS = 16,
    parameter integer C_CORDIC_FRAC_WIDTH = 32,
    parameter integer C_CORDIC_GAIN = 1304065751 // must be smaller than 32 bits for some reason
)(
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
    localparam integer C_CORDIC_LOG2_FRAC_WIDTH = $clog2(C_CORDIC_FRAC_WIDTH);
    localparam integer C_CORDIC_FIXED_WIDTH = (C_S00_AXIS_TDATA_WIDTH/2) + C_CORDIC_FRAC_WIDTH + 1; // +1 is hack to make everything positive

    logic [31:0] angles [0:15];
    //logic [31:0] C_CORDIC_GAIN;

    // debug variables
    logic [31:0] angle1;
    logic signed [31:0] x_i0,x_i1,x_i2,x_i3,x_i4,x_i5,x_i6,x_i7,x_i8,x_i9,x_i10,x_i11,x_i12,x_i13,x_i14,x_i15,x_i16;
    logic signed [31:0] y_i0,y_i1,y_i2,y_i3,y_i4,y_i5,y_i6,y_i7,y_i8,y_i9,y_i10,y_i11,y_i12,y_i13,y_i14,y_i15,y_i16;
    logic signed [31:0] z_i0,z_i1,z_i2,z_i3,z_i4,z_i5,z_i6,z_i7,z_i8,z_i9,z_i10,z_i11,z_i12,z_i13,z_i14,z_i15,z_i16;

    always_comb begin
        // x
        x_i0 = x_i[0];
        x_i1 = x_i[1];
        x_i2 = x_i[2];
        x_i3 = x_i[3];
        x_i4 = x_i[4];
        x_i5 = x_i[5];
        x_i6 = x_i[6];
        x_i7 = x_i[7];
        x_i8 = x_i[8];
        x_i9 = x_i[9];
        x_i10 = x_i[10];
        x_i11 = x_i[11];
        x_i12 = x_i[12];
        x_i13 = x_i[13];
        x_i14 = x_i[14];
        x_i15 = x_i[15];
        x_i16 = x_i[16];

        // y
        y_i0 = y_i[0];
        y_i1 = y_i[1];
        y_i2 = y_i[2];
        y_i3 = y_i[3];
        y_i4 = y_i[4];
        y_i5 = y_i[5];
        y_i6 = y_i[6];
        y_i7 = y_i[7];
        y_i8 = y_i[8];
        y_i9 = y_i[9];
        y_i10 = y_i[10];
        y_i11 = y_i[11];
        y_i12 = y_i[12];
        y_i13 = y_i[13];
        y_i14 = y_i[14];
        y_i15 = y_i[15];
        y_i16 = y_i[16];

        // z
        z_i0 = z_i[0];
        z_i1 = z_i[1];
        z_i2 = z_i[2];
        z_i3 = z_i[3];
        z_i4 = z_i[4];
        z_i5 = z_i[5];
        z_i6 = z_i[6];
        z_i7 = z_i[7];
        z_i8 = z_i[8];
        z_i9 = z_i[9];
        z_i10 = z_i[10];
        z_i11 = z_i[11];
        z_i12 = z_i[12];
        z_i13 = z_i[13];
        z_i14 = z_i[14];
        z_i15 = z_i[15];
        z_i16 = z_i[16];
    end

    assign angle1 = angles[0];
    // end debug variables

    initial begin
        angles[0] = 32'd536871365;
        angles[1] = 32'd316933673;
        angles[2] = 32'd167459048;
        angles[3] = 32'd85004827;
        angles[4] = 32'd42667367;
        angles[5] = 32'd21354483;
        angles[6] = 32'd10679847;
        angles[7] = 32'd5340249;
        angles[8] = 32'd2670165;
        angles[9] = 32'd1335087;
        angles[10] = 32'd667544;
        angles[11] = 32'd333772;
        angles[12] = 32'd166886;
        angles[13] = 32'd83443;
        angles[14] = 32'd41721;
        angles[15] = 32'd10430;
    end
    // Helper functions
    function logic [C_CORDIC_FIXED_WIDTH-1:0] rnd2zerodiv(
        input logic signed [C_CORDIC_FIXED_WIDTH-1:0] x,
        input logic [C_CORDIC_LOG2_FRAC_WIDTH-1:0] i
    );
        logic sign;
        if ($signed(x) < 0) begin
            x = -x;
            sign = 1;
        end else begin
            sign = 0;
        end

        x = x >> i;

        if (sign) begin
            rnd2zerodiv = -x;
        end else begin
            rnd2zerodiv = x;
        end
    endfunction

    // initial begin
    //     assert(C_CORDIC_FRAC_WIDTH == 16) else $fatal("C_CORDIC_FRAC_WIDTH must be 16, or fix the CORDIC gain const.");
    // end

    function logic [C_CORDIC_FIXED_WIDTH-1:0] abs_scale(
        input logic signed [C_S00_AXIS_TDATA_WIDTH/2-1:0] x
    );
        if ($signed(x) < 0) begin
            abs_scale = $signed(-x) * $signed(C_CORDIC_GAIN);
        end else begin
            abs_scale = x * C_CORDIC_GAIN;
        end
    endfunction

    // Pipeline registers
    logic signed [C_CORDIC_FIXED_WIDTH-1:0] x_i [0:C_NUM_CORDIC_ITERATIONS];
    logic signed [C_CORDIC_FIXED_WIDTH-1:0] y_i [0:C_NUM_CORDIC_ITERATIONS];
    logic signed [C_CORDIC_FIXED_WIDTH-1:0] z_i [0:C_NUM_CORDIC_ITERATIONS];
    logic  flips_i [0:C_NUM_CORDIC_ITERATIONS];
    logic y_neg_i [0:C_NUM_CORDIC_ITERATIONS];
    logic x_neg_i [0:C_NUM_CORDIC_ITERATIONS];
    logic tvalid_i [0:C_NUM_CORDIC_ITERATIONS];
    logic tlast_i [0:C_NUM_CORDIC_ITERATIONS];

    // Initial inputs (scale the absolute value)
    logic signed [C_S00_AXIS_TDATA_WIDTH/2:0] pre_x_i_0, pre_y_i_0;
    logic signed [C_S00_AXIS_TDATA_WIDTH/2-1:0] x_i_0, y_i_0, z_i_0;
    logic flips_i_0;
    logic y_neg;
    logic x_neg;
    assign pre_x_i_0 = $signed(s00_axis_tdata[(C_S00_AXIS_TDATA_WIDTH/2)-1:0]);
    assign pre_y_i_0 = $signed(s00_axis_tdata[(C_S00_AXIS_TDATA_WIDTH-1):(C_S00_AXIS_TDATA_WIDTH/2)]);
    assign x_i_0 = $signed(pre_x_i_0)<0?-pre_x_i_0:pre_x_i_0;
    assign y_i_0 = $signed(pre_x_i_0)<0?-pre_y_i_0:pre_y_i_0;
    assign z_i_0 = 0;
    assign flips_i_0 = (pre_x_i_0<=0 && pre_y_i_0<=0);
    assign y_neg = $signed(pre_y_i_0) < 0;
    assign x_neg = $signed(pre_x_i_0) < 0;
    always_ff @(posedge s00_axis_aclk) begin
        if (m00_axis_tready) begin
            tvalid_i[0] <= s00_axis_tvalid;
            tlast_i[0] <= s00_axis_tlast;
            x_i[0] <= abs_scale(x_i_0);
            y_i[0] <= abs_scale(y_i_0);
            z_i[0] <= 0;
            flips_i[0] <= flips_i_0;
            y_neg_i[0] <= y_neg;
            x_neg_i[0] <= x_neg;
        end
    end

    // Pipeline stages
    genvar i;
    generate for (i = 0; i < C_NUM_CORDIC_ITERATIONS; i = i + 1) begin: cordic_iteration
        always_ff @(posedge s00_axis_aclk) begin
            if (m00_axis_tready) begin
                tvalid_i[i+1] <= tvalid_i[i];
                tlast_i[i+1] <= tlast_i[i];
                flips_i[i+1] <= flips_i[i];
                y_neg_i[i+1] <= y_neg_i[i];
                x_neg_i[i+1] <= x_neg_i[i];
                if ($signed(y_i[i]) < 0) begin
                    x_i[i+1] <= x_i[i] - rnd2zerodiv(y_i[i], i);
                    y_i[i+1] <= y_i[i] + rnd2zerodiv(x_i[i], i);
                    z_i[i+1] <= $signed(z_i[i]) - $signed(angles[i]);
                end else begin
                    x_i[i+1] <= x_i[i] + rnd2zerodiv(y_i[i], i);
                    y_i[i+1] <= y_i[i] - rnd2zerodiv(x_i[i], i);
                    z_i[i+1] <= $signed(z_i[i]) + $signed(angles[i]);
                end
            end
        end
    end endgenerate

    logic [31:0] mag;
    logic [31:0] rotate_angle, regular_angle, y_neg_angle,x_neg_angle;
    assign rotate_angle     = z_i[C_NUM_CORDIC_ITERATIONS]-2147483648;
    assign regular_angle    =  z_i[C_NUM_CORDIC_ITERATIONS];
    assign y_neg_angle = 32'hffff_ffff - regular_angle;
    assign x_neg_angle = 32'hffff_ffff - rotate_angle;
    assign mag =  x_i[C_NUM_CORDIC_ITERATIONS][C_CORDIC_FIXED_WIDTH-2:C_CORDIC_FRAC_WIDTH-1]; // this is supposed to do the right shifting
    assign m00_axis_tvalid = tvalid_i[C_NUM_CORDIC_ITERATIONS];
    assign m00_axis_tlast = tlast_i[C_NUM_CORDIC_ITERATIONS];
    //assign m00_axis_tdata = x_i[C_NUM_CORDIC_ITERATIONS][C_CORDIC_FIXED_WIDTH-2:C_CORDIC_FRAC_WIDTH]; // remove the extra bit with -2 instead of -1
    always_comb begin
        if (flips_i[C_NUM_CORDIC_ITERATIONS]) begin
            m00_axis_tdata = {rotate_angle, mag};
        end else begin
            if(y_neg_i[C_NUM_CORDIC_ITERATIONS])begin
                m00_axis_tdata = {y_neg_angle, mag};
            end else if (x_neg_i[C_NUM_CORDIC_ITERATIONS]) begin
                m00_axis_tdata = {x_neg_angle, mag};
            end else begin
                m00_axis_tdata = {regular_angle, mag};
            end

        end
    end

    // Pass through ready and strb
    assign s00_axis_tready = m00_axis_tready;
    assign m00_axis_tstrb = 4'hf;
endmodule

`default_nettype wire
