
`timescale 1ns / 1ps
module cocotb_vivado_dump();
  initial begin
    $dumpfile("/home/yhawaz/radioHead/sim/sim_build/conj_demod.fst");
    $dumpvars(0,conj_demod);
  end
endmodule
