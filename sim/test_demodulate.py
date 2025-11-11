import cocotb
import os
import random
import sys
from math import log
import numpy
import logging
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import Timer, ClockCycles, RisingEdge, FallingEdge, ReadOnly,with_timeout, NextTimeStep
from cocotb.utils import get_sim_time as gst
from cocotb.runner import get_runner
from cocotb.handle import SimHandleBase

from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.scoreboard import Scoreboard
import numpy as np

from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db, coverage_section
import constraint
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
        else:
            if value.get("type")=="write_single":
                await falling_edge
                self.bus.axis_tvalid.value=1
                #dotting my eeys
                self.bus.axis_tstrb.value = 0xF
                self.bus.axis_tdata.value = value.get("contents")["data"]
                self.bus.axis_tlast.value = value.get("contents")["last"]
                while True:
                    if(self.bus.axis_tready.value==1):
                        break
                    await rising_edge

            if value.get("type")=="write_burst":
                trans=value.get("contents")["data"]
                for i in range(len(trans)) :
                    while True:
                        await falling_edge
                        self.bus.axis_tvalid.value=1
                        #dotting my eeys
                        self.bus.axis_tstrb.value = 0xF
                        self.bus.axis_tdata.value = int(trans[i])
                        self.bus.axis_tlast.value = (i==len(trans)-1)
                        await read_only
                        if(self.bus.axis_tready.value==1):
                            break
                        await rising_edge

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
        else:

            if value.get("type") == "read":
                beats=0
                done_beats=value.get("duration")
                self.bus.axis_tready.value=1
                while(beats<done_beats):
                    await falling_edge
                    await read_only
                    if(self.bus.axis_tvalid.value==1):
                        beats+=1
                    await rising_edge

async def reset(clk,rst, cycles_held = 3,polarity=1):
    rst.value = polarity
    await ClockCycles(clk, cycles_held)
    rst.value = not polarity

sig_in = []
sig_out_exp = [] #contains list of expected outputs (Growing)

def bit_2_degree(bit_angle):
	return (360*bit_angle)/(2**16)

def degree_2_bit(real_angle):
	return (real_angle/360)*(2**16)


def pack_complex(angle,mag):
	return ((int(angle) & 0xFFFF) << 16) | (int(mag) & 0xFFFF)

def unpack_complex(packed):
    angle = (packed >> 16) & 0xFFFF
    magnitude = packed & 0xFFFF
    return angle, magnitude

def demodulate_model(val):
    global prev_val
    sig_in.append(val)
    if(prev_val!=None):
        demod = 0.5 * np.angle(prev_val * np.conj(val))
    else:
    #idk how to handle first one being garbage tbh
		    demod= 0 
    sig_out_exp.append(demod)

@cocotb.test()
async def test_a(dut):
    """cocotb test for averager controller"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=demodulate_model)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk)
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port

    # Create a scoreboard on the stream_out bus
    scoreboard = Scoreboard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())

    #cocotb.start_soon(state_monitor(dut)) #feel free to bring back in
    #cocotb.start_soon(state_and_input_monitor(dut)) #feel free to bring back in
    cocotb.start_soon(os_monitor(dut))
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)

    for i in range(50):
        angle = random.randint(1,(2**16)-1)
        magnitude=random.randint(1,(2**16)-1)
        numby=pack_complex(angle,magnitude)
        data = {'type':'write_single', "contents":{"data": numby,"last":0}}
        ind.append(data)
        pause = {"type":"pause","duration":random.randint(1,6)}
        ind.append(pause)
        ind.append({'type':'write_burst', "contents": {"data": np.array(list(range(100)))}})
        ind.append({'type':'pause','duration':2}) #end with pause

    for i in range(50):
        outd.append({'type':'read', "duration":random.randint(1,10)})
        outd.append({'type':'pause', "duration":random.randint(1,10)})
    await ClockCycles(dut.s00_axis_aclk, 500)

    
    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv('sim_result', "./"), 'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :/"

def demodulate_runner():
    """Simulate the demodulate using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sys.path.append(str(proj_path / "hdl" ))
    sources = [proj_path / "hdl" / "demodulate.sv"]
    build_test_args = ["-Wall"]
    parameters = {} #!!!
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    hdl_toplevel = "demodulate"
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
   demodulate_runner()




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

async def drive_coeffs(dut,coeffs):
    #dut._log.info(f"Inputting the following coefficients to the FIR: {coeffs}")
    await FallingEdge(dut.s00_axis_aclk)

    # Setting the coefficients
    # code to put the packed array into a full 2d array:
    for i in range(15):
        for b in range(8):
            dut.coeffs[b+8*i].value = (coeffs[i]>>b)&0x1

sig_in = []
sig_out_exp = [] #contains list of expected outputs (Growing)
sig_out_act = [] #contains list of expected outputs (Growing)



def demodulate_model(val):
    global prev_val
    sig_in.append(val)
    if(prev_val!=None):
        demod = 0.5 * np.angle(prev_val * np.conj(val))
    else:
    #idk how to handle first one being garbage tbh
        demod = 0 
    sig_out_exp.append(demod)


@cocotb.test()
async def test_a(dut):
    global sig_in,sig_out_exp,sig_out_act
    """cocotb test for skid buffer no backpressure"""
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
    """cocotb test for AXIS Skid Buffer with sporadic backpressure"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=model_skid_buffer)
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
