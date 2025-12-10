`default_nettype none // prevents system from inferring an undeclared logic (good practice)
module pwm32(   input wire clk_in,
              input wire rst_in,
              input wire [31:0] dc_in,
              input wire d_valid,
              output logic sig_out);
 
    logic [63:0] count;
    logic [31:0] cur_dc;
    always @(posedge clk_in)begin
        if(d_valid)begin
            cur_dc <= dc_in;
        end 
    end

    counter mc (.clk_in(clk_in),
                .rst_in(rst_in),
                .period_in(32'd4294967295),
                .count_out(count));
    assign sig_out = count<cur_dc; //very simple threshold check
endmodule