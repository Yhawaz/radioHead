import cocotb
import os
import random
import sys
from math import log
import numpy
import logging
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles, RisingEdge, FallingEdge, ReadOnly,with_timeout
from cocotb.utils import get_sim_time as gst
from cocotb.runner import get_runner
from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.scoreboard import Scoreboard
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import lfilter,lfiltic

test_file = os.path.basename(__file__).replace(".py","")

class AXIS_Monitor(BusMonitor):
    """
    monitors axi streaming bus
    """
    transactions = 0 #use this variable to track good ready/valid handshakes
    def __init__(self, dut, name, clk, callback=None):
        self._signals = ['axis_tvalid','axis_tready','axis_tlast','axis_tdata','axis_tstrb']
        BusMonitor.__init__(self, dut, name, clk, callback=callback)
        self.clock = clk
        self.transactions = 0
        self.dut = dut
    async def _monitor_recv(self):
        """
        Monitor receiver
        """
        rising_edge = RisingEdge(self.clock) # make these coroutines once and reuse
        falling_edge = FallingEdge(self.clock)
        read_only = ReadOnly() #This is
        while True:
            #await rising_edge #can either wait for just edge...
            #or you can also wait for falling edge/read_only (see note in lab)
            await falling_edge #sometimes see in AXI shit
            await read_only  #readonly (the postline)
            valid = self.bus.axis_tvalid.value
            ready = self.bus.axis_tready.value
            last = self.bus.axis_tlast.value
            data = self.bus.axis_tdata.value #.signed_integer
            if valid and ready:
                self.transactions+=1
                thing = dict(data=data.signed_integer,last=last,
                             name=self.name,count=self.transactions)
                self.dut._log.info(f"{self.name}: {thing}")
                self._recv(data.signed_integer)

class AXIS_Driver(BusDriver):
    def __init__(self, dut, name, clk, role="M"):
        self._signals = ['axis_tvalid', 'axis_tready', 'axis_tlast', 'axis_tdata','axis_tstrb']
        BusDriver.__init__(self, dut, name, clk)
        self.clock = clk
        self.dut = dut

class M_AXIS_Driver(AXIS_Driver):
    def __init__(self, dut, name, clk):
        super().__init__(dut,name,clk)
        self.bus.axis_tdata.value = 0
        self.bus.axis_tstrb.value = 0xF
        self.bus.axis_tlast.value = 0
        self.bus.axis_tvalid.value = 0

    async def _driver_send(self, value, sync=True):
        rising_edge = RisingEdge(self.clock) # make these coroutines once and reuse
        falling_edge = FallingEdge(self.clock)
        read_only = ReadOnly() #This is
        if value.get("type") == "pause":
            await falling_edge
            self.bus.axis_tvalid.value = 0 #set to 0 and be done.
            self.bus.axis_tlast.value = 0 #set to 0 and be done.
            for i in range(value.get("duration",1)):
                await rising_edge
        elif value.get("type") == "write_single":
            await falling_edge
            cont = value.get("contents")
            self.bus.axis_tdata.value = cont.get("data")
            self.bus.axis_tlast.value = cont.get("last")
            self.bus.axis_tvalid.value = 1
            while True:
                await rising_edge
                if self.bus.axis_tready.value:
                    break
            self.bus.axis_tvalid.value = 0
        elif value.get("type") == "write_burst":
            arr = value.get("contents").get("data")
            arr_len = len(arr)
            for i in range(arr_len):
                await falling_edge
                self.bus.axis_tdata.value = int(arr[i])
                self.bus.axis_tvalid.value = 1
                if i == arr_len - 1 :
                    self.bus.axis_tlast.value = 1
                else:
                    self.bus.axis_tlast.value = 0
                while True:
                    await rising_edge
                    if self.bus.axis_tready.value:
                        break
            self.bus.axis_tvalid.value = 0

                    
                
                

class S_AXIS_Driver(BusDriver):
    def __init__(self, dut, name, clk):
        self._signals = ['axis_tvalid', 'axis_tready', 'axis_tlast', 'axis_tdata','axis_tstrb']
        AXIS_Driver.__init__(self, dut, name, clk)
        self.bus.axis_tready.value = 0

    async def _driver_send(self, value, sync=True):
        rising_edge = RisingEdge(self.clock) # make these coroutines once and reuse
        falling_edge = FallingEdge(self.clock)
        read_only = ReadOnly() #This is
        if value.get("type") == "pause":
            await falling_edge
            self.bus.axis_tready.value = 0 #set to 0 and be done.
            for i in range(value.get("duration",1)):
                await rising_edge
        elif value.get("type") == "read":
            await falling_edge
            self.bus.axis_tready.value = 1
            for i in range(value.get("duration",1)):
                while True:
                    await rising_edge
                    if self.bus.axis_tvalid.value:
                        break
            self.bus.axis_tready.value = 0
            

async def reset(clk,rst, cycles_held = 3,polarity=1):
    rst.value = polarity
    await ClockCycles(clk, cycles_held)
    rst.value = not polarity


sig_in = []
sig_out_exp = [] #contains list of expected outputs (Growing)
sig_out_act = [] #contains list of expected outputs (Growing)

#payloads = [1,0,1,0,0,1,0] # First test payload
payloads = [random.randint(0, 1) for _ in range(100)]
#payloads = [payload for i in range(5)]
last_bit = 0
count = 0

def manchester_encode_diff(current_bit):
    global last_bit
    """compute the differential manchester encoding of a bit"""
    decoded_bit = 1 if current_bit != last_bit else 0 # checking for change in bits
    last_bit = current_bit    
    return  decoded_bit

def model_manchester_decode_diff(sample):
    # you have to append one of the results to the sig out exp array
    global count,last_bit
    if count > 0: # First sample is trash
        sig_in.append(sample)
        sig_out_exp.append(manchester_encode_diff(sample))
    else:
        sig_in.append(sample)
        sig_out_exp.append(1 ^ sample)
        last_bit = sample
    count += 1


@cocotb.test()
async def test_a(dut):
    global sig_in,sig_out_exp,sig_out_act
    """cocotb test for manchester diff no backpressure"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=model_manchester_decode_diff)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: sig_out_act.append(x))
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port
    # Create a scoreboard on the stream_out bus
    scoreboard = Scoreboard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)


    # When feeding the data, ignore the output from the first thing
    #(pts)
    #assert 1 == 2
    #feed the driver on the M Side:
    # You can't give a list to the module
    # How does the module take in data?
    for i in range(len(payloads)):
        ind.append({'type':'write_single', "contents":{"data": payloads[i],"last":0}})
        ind.append({"type":"pause","duration":100})
    ind.append({'type':'write_burst', "contents": {"data": payloads}})
    ind.append({'type':'pause','duration':2}) #end with pause

    #feed the driver on the S Side:
    #always be ready to receive data:
    outd.append({'type':'read', "duration":10000100})

    await ClockCycles(dut.s00_axis_aclk, 20000)
    dut._log.info(f"In Transactions:{inm.transactions}, Out Transactions:{outm.transactions}")
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :-/ In: {inm.transactions}, Out: {outm.transactions}"

sig_in = []
sig_out_exp = [] #contains list of expected outputs (Growing)
sig_out_act = [] #contains list of expected outputs (Growing)

@cocotb.test()
async def test_b(dut):
    global sig_in,sig_out_exp,sig_out_act
    """cocotb test for manchester diff with sporadic backpressure"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=model_manchester_decode_diff)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: sig_out_act.append(x))
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port
    # Create a scoreboard on the stream_out bus
    scoreboard = Scoreboard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)


    #feed the driver on the M Side:
    #for i in range(50):
    for i in range(len(payloads)):
        data = {'type':'write_single', "contents":{"data": payloads[i],"last":0}}
        ind.append(data)
        pause = {"type":"pause","duration":random.randint(1,6)}
        ind.append(pause)
    ind.append({'type':'write_burst', "contents": {"data": payloads}})
    ind.append({'type':'pause','duration':5}) #end with pause
    #feed the driver on the S Side with on/off backpressure!
    for i in range(50):
        outd.append({'type':'read', "duration":random.randint(1,10)})
        outd.append({'type':'pause', "duration":random.randint(1,10)})
    await ClockCycles(dut.s00_axis_aclk, 1000)
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :-/ In: {inm.transactions}, Out: {outm.transactions}"

def diff_manchester_runner():
    """Simulate the Differential Manchester Decoding using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sys.path.append(str(proj_path / "hdl" ))
    sources = [proj_path / "hdl" / "diff_manchester.sv"]
    build_test_args = ["-Wall"]
    parameters = {} #!!!
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    hdl_toplevel = "diff_manchester"
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_toplevel, #fir_15
        always=True,
        build_args=build_test_args,
        parameters=parameters,
        timescale = ('1ns','1ps'),
        waves=True
    )
    run_test_args = []
    runner.test(
        hdl_toplevel=hdl_toplevel, #fir_15
        test_module=test_file,
        test_args=run_test_args,
        waves=True
    )
if __name__ == "__main__":
    diff_manchester_runner()
