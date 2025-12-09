module cocotb_iverilog_dump();
initial begin
    $dumpfile("/home/yabi/projs/radioHead/sim/sim_build/fm32bit_19kHz_filter.fst");
    $dumpvars(0, fm32bit_19kHz_filter);
end
endmodule
