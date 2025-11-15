module cocotb_iverilog_dump();
initial begin
    $dumpfile("/Users/yabi/Documents/Schooly_Stuff/6.s965/radioHead/sim/sim_build/demo_shim.fst");
    $dumpvars(0, demo_shim);
end
endmodule
