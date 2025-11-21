
`timescale 1ns / 1ps
module cocotb_vivado_dump();
  initial begin
    $dumpfile("/home/yhawaz/radioHead/sim/sim_build/demod64.fst");
    $dumpvars(0,demod64);
  end
endmodule
