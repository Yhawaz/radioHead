
`timescale 1ns / 1ps
module cocotb_vivado_dump();
  initial begin
    $dumpfile("/home/fpga/worker_place/temp/temp/e266dfd8cddc4b19bfe777093ab69fae/sim_build/conj_demod.fst");
    $dumpvars(0,conj_demod);
  end
endmodule
