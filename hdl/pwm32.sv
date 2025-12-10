`default_nettype none // prevents system from inferring an undeclared logic (good practice)
module pwm32(   input wire clk_in,
              input wire rst_in,
              input wire [31:0] dc_in,
              output logic sig_out);
 
    logic [63:0] count;
    counter mc (.clk_in(clk_in),
                .rst_in(rst_in),
                .period_in(4294967295),
                .count_out(count));
    assign sig_out = count<dc_in; //very simple threshold check
endmodule