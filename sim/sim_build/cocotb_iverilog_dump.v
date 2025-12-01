module cocotb_iverilog_dump();
initial begin
    $dumpfile("/home/yhawaz/radioHead/sim/sim_build/conj_demod.fst");
    $dumpvars(0, conj_demod);
end
endmodule
