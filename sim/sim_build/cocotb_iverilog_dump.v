module cocotb_iverilog_dump();
initial begin
    $dumpfile("/Users/yabi/Documents/Schooly_Stuff/6.s965/radioHead/sim/sim_build/conj_demod.fst");
    $dumpvars(0, conj_demod);
end
endmodule
