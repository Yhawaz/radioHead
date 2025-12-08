`timescale 1ns / 1ps
`default_nettype none
 
module axis_fir_15 #
    (
        parameter integer C_S00_AXIS_TDATA_WIDTH    = 64,
        parameter integer C_M00_AXIS_TDATA_WIDTH    = 32
    )
    (
 
        // Ports of Axi Slave Bus Interface S00_AXIS
        input wire  s00_axis_aclk, s00_axis_aresetn,
        input wire  s00_axis_tlast, s00_axis_tvalid,
        input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
        input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1: 0] s00_axis_tstrb,
        output logic  s00_axis_tready,
 
        // Ports of Axi Master Bus Interface M00_AXIS
        input wire  m00_axis_aclk, m00_axis_aresetn,
        input wire  m00_axis_tready,
        output logic  m00_axis_tvalid, m00_axis_tlast,
        output logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
        output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb
    );
 
    localparam NUM_COEFFS = 501;
    //i previously used some intermediate terms and then inialized them all
    //to zero
    logic signed [C_S00_AXIS_TDATA_WIDTH-1:0] intmdt_term [NUM_COEFFS -1:0];
    initial begin
        for(int i=0; i<NUM_COEFFS; i++)begin
            intmdt_term[i] = 0;
        end
        $display("DONE!");
    end

    logic signed [NUM_COEFFS-1:0][7:0] coeffs;
    // hardcoding all the coeffs for cutoff frequency of 6.25 kHz
    always_comb begin
        coeffs[0] = 8'sd1;
        coeffs[1] = 8'sd1;
        coeffs[2] = 8'sd1;
        coeffs[3] = 8'sd1;
        coeffs[4] = 8'sd1;
        coeffs[5] = 8'sd1;
        coeffs[6] = 8'sd1;
        coeffs[7] = 8'sd1;
        coeffs[8] = 8'sd1;
        coeffs[9] = 8'sd0;
        coeffs[10] = 8'sd0;
        coeffs[11] = -8'sd1;
        coeffs[12] = -8'sd1;
        coeffs[13] = -8'sd2;
        coeffs[14] = -8'sd3;
        coeffs[15] = -8'sd4;
        coeffs[16] = -8'sd6;
        coeffs[17] = -8'sd7;
        coeffs[18] = -8'sd8;
        coeffs[19] = -8'sd10;
        coeffs[20] = -8'sd11;
        coeffs[21] = -8'sd12;
        coeffs[22] = -8'sd12;
        coeffs[23] = -8'sd13;
        coeffs[24] = -8'sd13;
        coeffs[25] = -8'sd12;
        coeffs[26] = -8'sd11;
        coeffs[27] = -8'sd10;
        coeffs[28] = -8'sd7;
        coeffs[29] = -8'sd4;
        coeffs[30] = 8'sd0;
        coeffs[31] = 8'sd5;
        coeffs[32] = 8'sd10;
        coeffs[33] = 8'sd16;
        coeffs[34] = 8'sd23;
        coeffs[35] = 8'sd31;
        coeffs[36] = 8'sd39;
        coeffs[37] = 8'sd47;
        coeffs[38] = 8'sd56;
        coeffs[39] = 8'sd65;
        coeffs[40] = 8'sd74;
        coeffs[41] = 8'sd82;
        coeffs[42] = 8'sd91;
        coeffs[43] = 8'sd98;
        coeffs[44] = 8'sd105;
        coeffs[45] = 8'sd112;
        coeffs[46] = 8'sd117;
        coeffs[47] = 8'sd121;
        coeffs[48] = 8'sd124;
        coeffs[49] = 8'sd126;
        coeffs[50] = 8'sd127;
        coeffs[51] = 8'sd126;
        coeffs[52] = 8'sd124;
        coeffs[53] = 8'sd121;
        coeffs[54] = 8'sd117;
        coeffs[55] = 8'sd112;
        coeffs[56] = 8'sd105;
        coeffs[57] = 8'sd98;
        coeffs[58] = 8'sd91;
        coeffs[59] = 8'sd82;
        coeffs[60] = 8'sd74;
        coeffs[61] = 8'sd65;
        coeffs[62] = 8'sd56;
        coeffs[63] = 8'sd47;
        coeffs[64] = 8'sd39;
        coeffs[65] = 8'sd31;
        coeffs[66] = 8'sd23;
        coeffs[67] = 8'sd16;
        coeffs[68] = 8'sd10;
        coeffs[69] = 8'sd5;
        coeffs[70] = 8'sd0;
        coeffs[71] = -8'sd4;
        coeffs[72] = -8'sd7;
        coeffs[73] = -8'sd10;
        coeffs[74] = -8'sd11;
        coeffs[75] = -8'sd12;
        coeffs[76] = -8'sd13;
        coeffs[77] = -8'sd13;
        coeffs[78] = -8'sd12;
        coeffs[79] = -8'sd12;
        coeffs[80] = -8'sd11;
        coeffs[81] = -8'sd10;
        coeffs[82] = -8'sd8;
        coeffs[83] = -8'sd7;
        coeffs[84] = -8'sd6;
        coeffs[85] = -8'sd4;
        coeffs[86] = -8'sd3;
        coeffs[87] = -8'sd2;
        coeffs[88] = -8'sd1;
        coeffs[89] = -8'sd1;
        coeffs[90] = 8'sd0;
        coeffs[91] = 8'sd0;
        coeffs[92] = 8'sd1;
        coeffs[93] = 8'sd1;
        coeffs[94] = 8'sd1;
        coeffs[95] = 8'sd1;
        coeffs[96] = 8'sd1;
        coeffs[97] = 8'sd1;
        coeffs[98] = 8'sd1;
        coeffs[99] = 8'sd1;
        coeffs[100] = 8'sd1;
    end

    logic m00_axis_tvalid_reg, m00_axis_tlast_reg;
    logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata_reg;
    logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb_reg;

    assign s00_axis_tready = m00_axis_tready;

    logic valid_handshake;
    assign valid_handshake = m00_axis_tready & m00_axis_tvalid; 
 
    // FIR + AXIS Stuff

    always_ff @(posedge s00_axis_aclk)begin
        if(s00_axis_aresetn==0)begin
            // AXIS Stuff
            m00_axis_tvalid_reg <= 0;
            m00_axis_tlast_reg <= 0;
            m00_axis_tdata_reg <= 0;
            m00_axis_tstrb_reg <= 0;

            // FIR Stuff
            // no need to reset data out because that is AXIS
            // no need to reset data valid because that is AXIS
            for(int i=0; i<NUM_COEFFS; i++)begin
                intmdt_term[i] = 0;
            end
            // still need to reset all the intermediate terms
        end else begin
            if(s00_axis_tready && s00_axis_tvalid)begin
                // Only evolve state with new valid data input
                // FIR Stuff
                for(int i = 0; i<NUM_COEFFS;i++)begin
                    if(i == NUM_COEFFS-1)begin
                        intmdt_term[i] <= $signed(coeffs[i]) * $signed(s00_axis_tdata[63:32]); // s data should be data_in
                    end else begin
                        intmdt_term[i] <= $signed(coeffs[i]) * $signed(s00_axis_tdata[63:32]) + $signed(intmdt_term[i+1]);
                    end
                end

                m00_axis_tvalid <= 1'b1;
                m00_axis_tlast <= s00_axis_tlast;
                m00_axis_tdata <= $signed(intmdt_term[0]);
                m00_axis_tstrb <= s00_axis_tstrb;
            end
            else if(valid_handshake)begin
                m00_axis_tvalid <= 1'b0;
            end
            
        end
    end
    //assign s00_axis_tready = m00_axis_tready; //immediate (for now)
 
endmodule
 
`default_nettype wire
