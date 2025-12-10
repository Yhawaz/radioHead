`timescale 1ns / 1ps
`default_nettype none
 
module axis_fir_57khz #
    (
        parameter integer C_S00_AXIS_TDATA_WIDTH    = 64,
        parameter integer C_M00_AXIS_TDATA_WIDTH    = 64
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

        //input wire signed [NUM_COEFFS-1:0][7:0] coeffs
    );
 
    localparam NUM_COEFFS = 501;
    //i previously used some intermediate terms and then inialized them all
    //to zero
    logic signed [C_S00_AXIS_TDATA_WIDTH-1:0] intmdt_term [NUM_COEFFS -1:0];
    initial begin
        for(int i=0; i<NUM_COEFFS; i++)begin
            intmdt_term[i] = 64'sd0;
        end
        $display("DONE!");
    end

    logic signed [NUM_COEFFS-1:0][15:0] coeffs;
    // hardcoding all the coeffs for cutoff frequency of 6.25 kHz
    always_comb begin
        coeffs[0] = -16'sd153;
        coeffs[1] = -16'sd72;
        coeffs[2] = 16'sd94;
        coeffs[3] = -16'sd2;
        coeffs[4] = -16'sd18;
        coeffs[5] = -16'sd75;
        coeffs[6] = 16'sd57;
        coeffs[7] = 16'sd53;
        coeffs[8] = -16'sd11;
        coeffs[9] = -16'sd93;
        coeffs[10] = 16'sd10;
        coeffs[11] = 16'sd85;
        coeffs[12] = 16'sd29;
        coeffs[13] = -16'sd98;
        coeffs[14] = -16'sd49;
        coeffs[15] = 16'sd85;
        coeffs[16] = 16'sd83;
        coeffs[17] = -16'sd74;
        coeffs[18] = -16'sd106;
        coeffs[19] = 16'sd46;
        coeffs[20] = 16'sd128;
        coeffs[21] = -16'sd15;
        coeffs[22] = -16'sd139;
        coeffs[23] = -16'sd24;
        coeffs[24] = 16'sd141;
        coeffs[25] = 16'sd63;
        coeffs[26] = -16'sd130;
        coeffs[27] = -16'sd102;
        coeffs[28] = 16'sd108;
        coeffs[29] = 16'sd136;
        coeffs[30] = -16'sd74;
        coeffs[31] = -16'sd161;
        coeffs[32] = 16'sd33;
        coeffs[33] = 16'sd175;
        coeffs[34] = 16'sd14;
        coeffs[35] = -16'sd175;
        coeffs[36] = -16'sd62;
        coeffs[37] = 16'sd161;
        coeffs[38] = 16'sd106;
        coeffs[39] = -16'sd134;
        coeffs[40] = -16'sd144;
        coeffs[41] = 16'sd96;
        coeffs[42] = 16'sd170;
        coeffs[43] = -16'sd51;
        coeffs[44] = -16'sd183;
        coeffs[45] = 16'sd1;
        coeffs[46] = 16'sd181;
        coeffs[47] = 16'sd47;
        coeffs[48] = -16'sd166;
        coeffs[49] = -16'sd90;
        coeffs[50] = 16'sd138;
        coeffs[51] = 16'sd124;
        coeffs[52] = -16'sd100;
        coeffs[53] = -16'sd146;
        coeffs[54] = 16'sd58;
        coeffs[55] = 16'sd155;
        coeffs[56] = -16'sd15;
        coeffs[57] = -16'sd150;
        coeffs[58] = -16'sd25;
        coeffs[59] = 16'sd134;
        coeffs[60] = 16'sd57;
        coeffs[61] = -16'sd109;
        coeffs[62] = -16'sd80;
        coeffs[63] = 16'sd79;
        coeffs[64] = 16'sd92;
        coeffs[65] = -16'sd47;
        coeffs[66] = -16'sd92;
        coeffs[67] = 16'sd19;
        coeffs[68] = 16'sd83;
        coeffs[69] = 16'sd4;
        coeffs[70] = -16'sd67;
        coeffs[71] = -16'sd18;
        coeffs[72] = 16'sd49;
        coeffs[73] = 16'sd23;
        coeffs[74] = -16'sd30;
        coeffs[75] = -16'sd19;
        coeffs[76] = 16'sd16;
        coeffs[77] = 16'sd9;
        coeffs[78] = -16'sd8;
        coeffs[79] = 16'sd5;
        coeffs[80] = 16'sd8;
        coeffs[81] = -16'sd19;
        coeffs[82] = -16'sd16;
        coeffs[83] = 16'sd30;
        coeffs[84] = 16'sd31;
        coeffs[85] = -16'sd34;
        coeffs[86] = -16'sd51;
        coeffs[87] = 16'sd30;
        coeffs[88] = 16'sd71;
        coeffs[89] = -16'sd17;
        coeffs[90] = -16'sd89;
        coeffs[91] = -16'sd5;
        coeffs[92] = 16'sd101;
        coeffs[93] = 16'sd34;
        coeffs[94] = -16'sd103;
        coeffs[95] = -16'sd66;
        coeffs[96] = 16'sd95;
        coeffs[97] = 16'sd98;
        coeffs[98] = -16'sd75;
        coeffs[99] = -16'sd125;
        coeffs[100] = 16'sd45;
        coeffs[101] = 16'sd143;
        coeffs[102] = -16'sd8;
        coeffs[103] = -16'sd151;
        coeffs[104] = -16'sd33;
        coeffs[105] = 16'sd145;
        coeffs[106] = 16'sd73;
        coeffs[107] = -16'sd128;
        coeffs[108] = -16'sd107;
        coeffs[109] = 16'sd99;
        coeffs[110] = 16'sd133;
        coeffs[111] = -16'sd62;
        coeffs[112] = -16'sd147;
        coeffs[113] = 16'sd22;
        coeffs[114] = 16'sd148;
        coeffs[115] = 16'sd18;
        coeffs[116] = -16'sd136;
        coeffs[117] = -16'sd52;
        coeffs[118] = 16'sd114;
        coeffs[119] = 16'sd78;
        coeffs[120] = -16'sd86;
        coeffs[121] = -16'sd92;
        coeffs[122] = 16'sd54;
        coeffs[123] = 16'sd95;
        coeffs[124] = -16'sd24;
        coeffs[125] = -16'sd87;
        coeffs[126] = 16'sd0;
        coeffs[127] = 16'sd71;
        coeffs[128] = 16'sd15;
        coeffs[129] = -16'sd51;
        coeffs[130] = -16'sd20;
        coeffs[131] = 16'sd31;
        coeffs[132] = 16'sd14;
        coeffs[133] = -16'sd15;
        coeffs[134] = -16'sd1;
        coeffs[135] = 16'sd8;
        coeffs[136] = -16'sd17;
        coeffs[137] = -16'sd10;
        coeffs[138] = 16'sd35;
        coeffs[139] = 16'sd24;
        coeffs[140] = -16'sd49;
        coeffs[141] = -16'sd46;
        coeffs[142] = 16'sd54;
        coeffs[143] = 16'sd75;
        coeffs[144] = -16'sd48;
        coeffs[145] = -16'sd106;
        coeffs[146] = 16'sd27;
        coeffs[147] = 16'sd133;
        coeffs[148] = 16'sd5;
        coeffs[149] = -16'sd150;
        coeffs[150] = -16'sd49;
        coeffs[151] = 16'sd155;
        coeffs[152] = 16'sd97;
        coeffs[153] = -16'sd143;
        coeffs[154] = -16'sd146;
        coeffs[155] = 16'sd114;
        coeffs[156] = 16'sd189;
        coeffs[157] = -16'sd68;
        coeffs[158] = -16'sd219;
        coeffs[159] = 16'sd11;
        coeffs[160] = 16'sd232;
        coeffs[161] = 16'sd53;
        coeffs[162] = -16'sd226;
        coeffs[163] = -16'sd116;
        coeffs[164] = 16'sd199;
        coeffs[165] = 16'sd173;
        coeffs[166] = -16'sd154;
        coeffs[167] = -16'sd215;
        coeffs[168] = 16'sd95;
        coeffs[169] = 16'sd240;
        coeffs[170] = -16'sd29;
        coeffs[171] = -16'sd243;
        coeffs[172] = -16'sd37;
        coeffs[173] = 16'sd225;
        coeffs[174] = 16'sd95;
        coeffs[175] = -16'sd189;
        coeffs[176] = -16'sd140;
        coeffs[177] = 16'sd140;
        coeffs[178] = 16'sd166;
        coeffs[179] = -16'sd85;
        coeffs[180] = -16'sd171;
        coeffs[181] = 16'sd32;
        coeffs[182] = 16'sd158;
        coeffs[183] = 16'sd12;
        coeffs[184] = -16'sd129;
        coeffs[185] = -16'sd40;
        coeffs[186] = 16'sd91;
        coeffs[187] = 16'sd49;
        coeffs[188] = -16'sd53;
        coeffs[189] = -16'sd39;
        coeffs[190] = 16'sd22;
        coeffs[191] = 16'sd13;
        coeffs[192] = -16'sd5;
        coeffs[193] = 16'sd24;
        coeffs[194] = 16'sd9;
        coeffs[195] = -16'sd63;
        coeffs[196] = -16'sd36;
        coeffs[197] = 16'sd94;
        coeffs[198] = 16'sd83;
        coeffs[199] = -16'sd109;
        coeffs[200] = -16'sd145;
        coeffs[201] = 16'sd98;
        coeffs[202] = 16'sd214;
        coeffs[203] = -16'sd58;
        coeffs[204] = -16'sd279;
        coeffs[205] = -16'sd14;
        coeffs[206] = 16'sd326;
        coeffs[207] = 16'sd112;
        coeffs[208] = -16'sd344;
        coeffs[209] = -16'sd230;
        coeffs[210] = 16'sd325;
        coeffs[211] = 16'sd354;
        coeffs[212] = -16'sd261;
        coeffs[213] = -16'sd470;
        coeffs[214] = 16'sd153;
        coeffs[215] = 16'sd562;
        coeffs[216] = -16'sd6;
        coeffs[217] = -16'sd615;
        coeffs[218] = -16'sd171;
        coeffs[219] = 16'sd617;
        coeffs[220] = 16'sd361;
        coeffs[221] = -16'sd559;
        coeffs[222] = -16'sd546;
        coeffs[223] = 16'sd441;
        coeffs[224] = 16'sd706;
        coeffs[225] = -16'sd266;
        coeffs[226] = -16'sd821;
        coeffs[227] = 16'sd48;
        coeffs[228] = 16'sd877;
        coeffs[229] = 16'sd198;
        coeffs[230] = -16'sd860;
        coeffs[231] = -16'sd450;
        coeffs[232] = 16'sd768;
        coeffs[233] = 16'sd683;
        coeffs[234] = -16'sd602;
        coeffs[235] = -16'sd875;
        coeffs[236] = 16'sd375;
        coeffs[237] = 16'sd1005;
        coeffs[238] = -16'sd102;
        coeffs[239] = -16'sd1058;
        coeffs[240] = -16'sd192;
        coeffs[241] = 16'sd1026;
        coeffs[242] = 16'sd482;
        coeffs[243] = -16'sd907;
        coeffs[244] = -16'sd741;
        coeffs[245] = 16'sd711;
        coeffs[246] = 16'sd947;
        coeffs[247] = -16'sd453;
        coeffs[248] = -16'sd1078;
        coeffs[249] = 16'sd156;
        coeffs[250] = 16'sd1123;
        coeffs[251] = 16'sd156;
        coeffs[252] = -16'sd1078;
        coeffs[253] = -16'sd453;
        coeffs[254] = 16'sd947;
        coeffs[255] = 16'sd711;
        coeffs[256] = -16'sd741;
        coeffs[257] = -16'sd907;
        coeffs[258] = 16'sd482;
        coeffs[259] = 16'sd1026;
        coeffs[260] = -16'sd192;
        coeffs[261] = -16'sd1058;
        coeffs[262] = -16'sd102;
        coeffs[263] = 16'sd1005;
        coeffs[264] = 16'sd375;
        coeffs[265] = -16'sd875;
        coeffs[266] = -16'sd602;
        coeffs[267] = 16'sd683;
        coeffs[268] = 16'sd768;
        coeffs[269] = -16'sd450;
        coeffs[270] = -16'sd860;
        coeffs[271] = 16'sd198;
        coeffs[272] = 16'sd877;
        coeffs[273] = 16'sd48;
        coeffs[274] = -16'sd821;
        coeffs[275] = -16'sd266;
        coeffs[276] = 16'sd706;
        coeffs[277] = 16'sd441;
        coeffs[278] = -16'sd546;
        coeffs[279] = -16'sd559;
        coeffs[280] = 16'sd361;
        coeffs[281] = 16'sd617;
        coeffs[282] = -16'sd171;
        coeffs[283] = -16'sd615;
        coeffs[284] = -16'sd6;
        coeffs[285] = 16'sd562;
        coeffs[286] = 16'sd153;
        coeffs[287] = -16'sd470;
        coeffs[288] = -16'sd261;
        coeffs[289] = 16'sd354;
        coeffs[290] = 16'sd325;
        coeffs[291] = -16'sd230;
        coeffs[292] = -16'sd344;
        coeffs[293] = 16'sd112;
        coeffs[294] = 16'sd326;
        coeffs[295] = -16'sd14;
        coeffs[296] = -16'sd279;
        coeffs[297] = -16'sd58;
        coeffs[298] = 16'sd214;
        coeffs[299] = 16'sd98;
        coeffs[300] = -16'sd145;
        coeffs[301] = -16'sd109;
        coeffs[302] = 16'sd83;
        coeffs[303] = 16'sd94;
        coeffs[304] = -16'sd36;
        coeffs[305] = -16'sd63;
        coeffs[306] = 16'sd9;
        coeffs[307] = 16'sd24;
        coeffs[308] = -16'sd5;
        coeffs[309] = 16'sd13;
        coeffs[310] = 16'sd22;
        coeffs[311] = -16'sd39;
        coeffs[312] = -16'sd53;
        coeffs[313] = 16'sd49;
        coeffs[314] = 16'sd91;
        coeffs[315] = -16'sd40;
        coeffs[316] = -16'sd129;
        coeffs[317] = 16'sd12;
        coeffs[318] = 16'sd158;
        coeffs[319] = 16'sd32;
        coeffs[320] = -16'sd171;
        coeffs[321] = -16'sd85;
        coeffs[322] = 16'sd166;
        coeffs[323] = 16'sd140;
        coeffs[324] = -16'sd140;
        coeffs[325] = -16'sd189;
        coeffs[326] = 16'sd95;
        coeffs[327] = 16'sd225;
        coeffs[328] = -16'sd37;
        coeffs[329] = -16'sd243;
        coeffs[330] = -16'sd29;
        coeffs[331] = 16'sd240;
        coeffs[332] = 16'sd95;
        coeffs[333] = -16'sd215;
        coeffs[334] = -16'sd154;
        coeffs[335] = 16'sd173;
        coeffs[336] = 16'sd199;
        coeffs[337] = -16'sd116;
        coeffs[338] = -16'sd226;
        coeffs[339] = 16'sd53;
        coeffs[340] = 16'sd232;
        coeffs[341] = 16'sd11;
        coeffs[342] = -16'sd219;
        coeffs[343] = -16'sd68;
        coeffs[344] = 16'sd189;
        coeffs[345] = 16'sd114;
        coeffs[346] = -16'sd146;
        coeffs[347] = -16'sd143;
        coeffs[348] = 16'sd97;
        coeffs[349] = 16'sd155;
        coeffs[350] = -16'sd49;
        coeffs[351] = -16'sd150;
        coeffs[352] = 16'sd5;
        coeffs[353] = 16'sd133;
        coeffs[354] = 16'sd27;
        coeffs[355] = -16'sd106;
        coeffs[356] = -16'sd48;
        coeffs[357] = 16'sd75;
        coeffs[358] = 16'sd54;
        coeffs[359] = -16'sd46;
        coeffs[360] = -16'sd49;
        coeffs[361] = 16'sd24;
        coeffs[362] = 16'sd35;
        coeffs[363] = -16'sd10;
        coeffs[364] = -16'sd17;
        coeffs[365] = 16'sd8;
        coeffs[366] = -16'sd1;
        coeffs[367] = -16'sd15;
        coeffs[368] = 16'sd14;
        coeffs[369] = 16'sd31;
        coeffs[370] = -16'sd20;
        coeffs[371] = -16'sd51;
        coeffs[372] = 16'sd15;
        coeffs[373] = 16'sd71;
        coeffs[374] = 16'sd0;
        coeffs[375] = -16'sd87;
        coeffs[376] = -16'sd24;
        coeffs[377] = 16'sd95;
        coeffs[378] = 16'sd54;
        coeffs[379] = -16'sd92;
        coeffs[380] = -16'sd86;
        coeffs[381] = 16'sd78;
        coeffs[382] = 16'sd114;
        coeffs[383] = -16'sd52;
        coeffs[384] = -16'sd136;
        coeffs[385] = 16'sd18;
        coeffs[386] = 16'sd148;
        coeffs[387] = 16'sd22;
        coeffs[388] = -16'sd147;
        coeffs[389] = -16'sd62;
        coeffs[390] = 16'sd133;
        coeffs[391] = 16'sd99;
        coeffs[392] = -16'sd107;
        coeffs[393] = -16'sd128;
        coeffs[394] = 16'sd73;
        coeffs[395] = 16'sd145;
        coeffs[396] = -16'sd33;
        coeffs[397] = -16'sd151;
        coeffs[398] = -16'sd8;
        coeffs[399] = 16'sd143;
        coeffs[400] = 16'sd45;
        coeffs[401] = -16'sd125;
        coeffs[402] = -16'sd75;
        coeffs[403] = 16'sd98;
        coeffs[404] = 16'sd95;
        coeffs[405] = -16'sd66;
        coeffs[406] = -16'sd103;
        coeffs[407] = 16'sd34;
        coeffs[408] = 16'sd101;
        coeffs[409] = -16'sd5;
        coeffs[410] = -16'sd89;
        coeffs[411] = -16'sd17;
        coeffs[412] = 16'sd71;
        coeffs[413] = 16'sd30;
        coeffs[414] = -16'sd51;
        coeffs[415] = -16'sd34;
        coeffs[416] = 16'sd31;
        coeffs[417] = 16'sd30;
        coeffs[418] = -16'sd16;
        coeffs[419] = -16'sd19;
        coeffs[420] = 16'sd8;
        coeffs[421] = 16'sd5;
        coeffs[422] = -16'sd8;
        coeffs[423] = 16'sd9;
        coeffs[424] = 16'sd16;
        coeffs[425] = -16'sd19;
        coeffs[426] = -16'sd30;
        coeffs[427] = 16'sd23;
        coeffs[428] = 16'sd49;
        coeffs[429] = -16'sd18;
        coeffs[430] = -16'sd67;
        coeffs[431] = 16'sd4;
        coeffs[432] = 16'sd83;
        coeffs[433] = 16'sd19;
        coeffs[434] = -16'sd92;
        coeffs[435] = -16'sd47;
        coeffs[436] = 16'sd92;
        coeffs[437] = 16'sd79;
        coeffs[438] = -16'sd80;
        coeffs[439] = -16'sd109;
        coeffs[440] = 16'sd57;
        coeffs[441] = 16'sd134;
        coeffs[442] = -16'sd25;
        coeffs[443] = -16'sd150;
        coeffs[444] = -16'sd15;
        coeffs[445] = 16'sd155;
        coeffs[446] = 16'sd58;
        coeffs[447] = -16'sd146;
        coeffs[448] = -16'sd100;
        coeffs[449] = 16'sd124;
        coeffs[450] = 16'sd138;
        coeffs[451] = -16'sd90;
        coeffs[452] = -16'sd166;
        coeffs[453] = 16'sd47;
        coeffs[454] = 16'sd181;
        coeffs[455] = 16'sd1;
        coeffs[456] = -16'sd183;
        coeffs[457] = -16'sd51;
        coeffs[458] = 16'sd170;
        coeffs[459] = 16'sd96;
        coeffs[460] = -16'sd144;
        coeffs[461] = -16'sd134;
        coeffs[462] = 16'sd106;
        coeffs[463] = 16'sd161;
        coeffs[464] = -16'sd62;
        coeffs[465] = -16'sd175;
        coeffs[466] = 16'sd14;
        coeffs[467] = 16'sd175;
        coeffs[468] = 16'sd33;
        coeffs[469] = -16'sd161;
        coeffs[470] = -16'sd74;
        coeffs[471] = 16'sd136;
        coeffs[472] = 16'sd108;
        coeffs[473] = -16'sd102;
        coeffs[474] = -16'sd130;
        coeffs[475] = 16'sd63;
        coeffs[476] = 16'sd141;
        coeffs[477] = -16'sd24;
        coeffs[478] = -16'sd139;
        coeffs[479] = -16'sd15;
        coeffs[480] = 16'sd128;
        coeffs[481] = 16'sd46;
        coeffs[482] = -16'sd106;
        coeffs[483] = -16'sd74;
        coeffs[484] = 16'sd83;
        coeffs[485] = 16'sd85;
        coeffs[486] = -16'sd49;
        coeffs[487] = -16'sd98;
        coeffs[488] = 16'sd29;
        coeffs[489] = 16'sd85;
        coeffs[490] = 16'sd10;
        coeffs[491] = -16'sd93;
        coeffs[492] = -16'sd11;
        coeffs[493] = 16'sd53;
        coeffs[494] = 16'sd57;
        coeffs[495] = -16'sd75;
        coeffs[496] = -16'sd18;
        coeffs[497] = -16'sd2;
        coeffs[498] = 16'sd94;
        coeffs[499] = -16'sd72;
        coeffs[500] = -16'sd153;
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