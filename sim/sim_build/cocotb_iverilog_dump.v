module cocotb_iverilog_dump();
initial begin
    $dumpfile("/home/yabi/projs/radioHead/sim/sim_build/fm32_filter.fst");
    $dumpvars(0, fm32_filter);
end
endmodule
