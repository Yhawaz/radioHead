`timescale 1ns / 1ps



module pwm_w(
        input wire clk,
        input wire rst,
        input wire [31:0] data_in,
        input wire valid_data_in,
        input wire [3:0] sh_amt,
        output wire sig_out
    );
    
    pwm sound_guy (
        .clk(clk),
        .rst(rst),
        .data_in(data_in),
        .valid_data_in(valid_data_in),
        .sh_amt(sh_amt),
        .sig_out(sig_out)
    );
endmodule
