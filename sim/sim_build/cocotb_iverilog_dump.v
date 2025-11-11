module cocotb_iverilog_dump();
initial begin
    $dumpfile("/Users/yabi/Documents/Schooly_Stuff/6.s965/radioHead/sim/sim_build/demodulate.fst");
    $dumpvars(0, demodulate);
end
endmodule
