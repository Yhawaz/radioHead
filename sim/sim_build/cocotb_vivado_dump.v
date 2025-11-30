
`timescale 1ns / 1ps
module cocotb_vivado_dump();
  initial begin
    $dumpfile("/home/yabi/projs/radioHead/sim/sim_build/demo_shim.fst");
    $dumpvars(0,demo_shim);
  end
endmodule
