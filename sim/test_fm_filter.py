import cocotb
import os
import random
import sys
import logging
from pathlib import Path
from cocotb.triggers import Timer, ClockCycles, RisingEdge, FallingEdge, ReadOnly,with_timeout, First, Join, ReadWrite, Edge
from cocotb.clock import Clock
from cocotb.utils import get_sim_time as gst
from cocotb.runner import get_runner
from cocotb.utils import get_sim_time

import numpy as np
from numpy.fft import fft
from scipy.signal import resample_poly, firwin, bilinear, lfilter
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import scipy
 
#cheap way to get the name of current file for runner:
test_file = os.path.basename(__file__).replace(".py","")



async def drive_reset(rst_val):
    rst_val.value=1
    await Timer(30,"ns")
    rst_val.value=0
    await Timer(10,"ns")

@cocotb.test()
async def first_test(dut):
    rawr=[]
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start(start_high=False))
    dut.trigger.value=0
    dut.rst.value=0
    dut.data_in.value=0
    received_messages = []
    cocotb.start_soon(model_spi_device(dut,received_messages) )
    cocotb.start_soon(assert_spi_clk(dut))
    await ClockCycles(dut.clk,1)
    await drive_reset(dut.rst)
    dut.clk_enable.value=1
    dut.validIn.value=1
    for(i in range(len(1000))):
        dut.dataIn.value=
        if(dut.validOut.value==1):
            rawr.append(dut.dataOut.value)
    
            
            
        


# boiler plate
"""the code below should largely remain unchanged in structure, though the specific files and things
specified should get updated for different simulations.
"""
def fm_filter_runner():
    """Simulate the fm_filter using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sources = [proj_path / "hdl" / "fm_filter.sv"] #grow/modify this as needed.
    hdl_toplevel = "fm_filter"
    build_test_args = ["-Wall"]#,"COCOTB_RESOLVE_X=ZEROS"]
    parameters = {}
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_toplevel,
        always=True,
        build_args=build_test_args,
        parameters=parameters,
        timescale = ('1ns','1ps'),
        waves=True
    )
    run_test_args = []
    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module=test_file,
        test_args=run_test_args,
        waves=True
    )
 
if __name__ == "__main__":
    fm_filter_runner()

