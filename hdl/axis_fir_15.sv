`default_nettype none
 
module axis_fir_15 #
    (
        parameter integer C_S00_AXIS_TDATA_WIDTH    = 32,
        parameter integer C_M00_AXIS_TDATA_WIDTH    = 32
    )
    (
 
        // Ports of Axi Slave Bus Interface S00_AXIS
        input wire  s00_axis_aclk, s00_axis_aresetn,
        input wire  s00_axis_tlast, s00_axis_tvalid,
        input wire [C_S00_AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
        input wire [(C_S00_AXIS_TDATA_WIDTH/8)-1: 0] s00_axis_tstrb,
        output logic  s00_axis_tready,
 
        //FIR coefficients:
        input wire signed [NUM_COEFFS-1:0][7:0] coeffs,
 
        // Ports of Axi Master Bus Interface M00_AXIS
        input wire  m00_axis_aclk, m00_axis_aresetn,
        input wire  m00_axis_tready,
        output logic  m00_axis_tvalid, m00_axis_tlast,
        output logic [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
        output logic [(C_M00_AXIS_TDATA_WIDTH/8)-1: 0] m00_axis_tstrb
    );
 
    localparam NUM_COEFFS = 101;
    //i previously used some intermediate terms and then inialized them all
    //to zero
    logic signed [31:0] intmdt_term [NUM_COEFFS -1:0];
    initial begin
        for(int i=0; i<NUM_COEFFS; i++)begin
            intmdt_term[i] = 0;
        end
        $display("DONE!");
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
                        intmdt_term[i] <= $signed(coeffs[i]) * $signed(s00_axis_tdata); // s data should be data_in
                    end else begin
                        intmdt_term[i] <= $signed(coeffs[i]) * $signed(s00_axis_tdata) + $signed(intmdt_term[i+1]);
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