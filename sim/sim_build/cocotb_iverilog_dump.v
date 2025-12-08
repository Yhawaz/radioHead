module cocotb_iverilog_dump();
initial begin
    $dumpfile("/home/yabi/projs/radioHead/sim/sim_build/fm_filter.fst");
    $dumpvars(0, fm_filter);
end
endmodule
