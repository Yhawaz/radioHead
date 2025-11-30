
`timescale 1ns / 1ps
`default_nettype none
module costas_loop #(
    parameter integer C_S00_AXIS_TDATA_WIDTH = 32,
    parameter integer C_M00_AXIS_TDATA_WIDTH = 32,
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

    // TODO: Then a LPF will be used to filter for the RDS im 
    //eh ig thats a way to think about it


    //im not doing these
    // TODO: Decimate data also
    // TODO: also resample the signal to 19 kHz
    //^idk wtf this dude is talking about im implementing thepysdr control loop so
        //rotate incoming iq signal by our "phase" estimate
        //calculate our error and phase estimate
    logic [16:0] beta;
    logic [16:0] alpha;
    logic [16:0] phase;
    logic [16:0] freq;

    always_comb begin
    
        //TODO FIGURE THIS LINE TF OUT out= s00_axis_tdata*nco(phase);
        //mixing is a muliplying the signals by their complex values, fuck my CHUNGUS LIFE
        error = new_i*new_q; 
    end

    always_ff @(posedge s00_axis_aclk)begin
       if(!s00_axis_aresetn)begin
           // don't do anything
           m00_axis_tvalid <= 0;
           m00_axis_tdata <= 0;
           //m00_axis_tstrb <= 0;
           m00_axis_tlast <= 0;
       end else begin
           if(s00_axis_tvalid && s00_axis_tready)begin
               // grab valid data and compute the difference
               val_reg <= s00_axis_tdata;
               m00_axis_tdata <= 
               m00_axis_tvalid <= 1'b1;
               m00_axis_tlast <= s00_axis_tlast;
               m00_axis_tstrb <= 255;
              //recalc stateful things
                //there is no way in gods green fucking earth we need to pipeline this im gonna sob 
               phase<=phase+freq+(alpha*error);
               freq<=freq+freq+(beta*error);
           end else begin
                    m00_axis_tvalid <= 1'b0;
           end
       end
    end
        

endmodule

`default_nettype wire
