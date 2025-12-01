`default_nettype none // prevents system from inferring an undeclared logic (good practice)

module pwm(   input wire clk_in,
              input wire rst_in,
              input wire [7:0] dc_in,
              output logic sig_out);
 
    logic [31:0] count;
    counter mc (.clk_in(clk_in),
                .rst_in(rst_in),
                .period_in(100000/255), // number of cycles, not the value of the period in ns
                .count_out(count));
    assign sig_out = count<dc_in; //very simple threshold check
endmodule

`default_nettype wire
