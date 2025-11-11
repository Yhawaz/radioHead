module cocotb_iverilog_dump();
initial begin
    $dumpfile("/Users/yabi/Documents/Schooly_Stuff/6.s965/radioHead/sim/sim_build/diff_manchester.fst");
    $dumpvars(0, diff_manchester);
end
endmodule
