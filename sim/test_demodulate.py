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


#SC = coverage_section (
#CoverPoint("top.st.state",
#            xf=lambda s, ns: s,
#            bins=['EMPTY', 'BUSY', 'FULL']
#            ),
#CoverPoint("top.st.next_state",
#            xf=lambda s, ns: ns,
#            bins=['EMPTY', 'BUSY', 'FULL']
#            ),
#CoverCross("top.st.state.cross",
#            items=["top.st.state", "top.st.next_state"],
#           ign_bins=[('FULL','EMPTY'), ('EMPTY','FULL')]
#           )
#)
#
#@SC
#def sampling_function(s,ns):
#    #could maybe do some work on these things right here.
#    pass
#
#async def state_monitor(dut):
#    states = {0:'EMPTY', 1:'BUSY', 2:'FULL'}
#    read_only = ReadOnly() #This is
#    falling_edge = FallingEdge(dut.s00_axis_aclk)
#    rising_edge = RisingEdge(dut.s00_axis_aclk)

#    await read_only
#    old_state = dut.state.value
#    while True:
#        await rising_edge #when module would change
#        await read_only
#        state = dut.state.value
#        sampling_function(states[old_state], states[state])
#        old_state = state
#
#STS = coverage_section(
#CoverPoint("top.st_sig.state",
#            xf=lambda state,sig: state,
#            bins=['EMPTY', 'BUSY', 'FULL']
#            ),
#CoverPoint("top.st_sig.s00_tvalid",
#            xf=lambda state,sig: sig.get('s00_tvalid'),
#            bins=[True, False]
#            ),
#CoverPoint("top.st_sig.s00_tready",
#            xf=lambda state,sig: sig.get('s00_tready'),
#            bins=[True, False]
#            ),
#CoverPoint("top.st_sig.m00_tvalid",
#            xf=lambda state,sig: sig.get('m00_tvalid'),
#            bins=[True, False]
#            ),
#CoverPoint("top.st_sig.m00_tready",
#            xf=lambda state,sig: sig.get('m00_tready'),
#            bins=[True, False]
#            ),
##CoverCross("top.st_sig.cross",
##            items=[ "top.st_sig.state",
##                    "top.st_sig.s00_tvalid",
##                    "top.st_sig.s00_tready",
##                    "top.st_sig.m00_tvalid",
##                    "top.st_sig.m00_tready"],
#           #ign_bins = [('FULL', False, True), ('FULL', False, False)]
##            )
#CoverCross("top.st_sig.scross",
#            items=[ "top.st_sig.state",
#                    "top.st_sig.s00_tvalid",
#                    "top.st_sig.s00_tready"],
#           ign_bins = [('EMPTY', True, False), ('EMPTY', False, False)]
#            ),
#CoverCross("top.st_sig.mcross",
#            items=[ "top.st_sig.state",
#                    "top.st_sig.m00_tvalid",
#                    "top.st_sig.m00_tready"],
#           ign_bins = [('FULL', False, True), ('FULL', False, False)]
#            )
#)
#
#@STS
#def sts_sampling_function(state,sig):
#  pass
#
#async def state_and_input_monitor(dut):
#    states = {0:'EMPTY', 1:'BUSY', 2:'FULL'}
#    read_only = ReadOnly()
#    falling_edge = FallingEdge(dut.s00_axis_aclk)
#    rising_edge = RisingEdge(dut.s00_axis_aclk)
#    await read_only
#    old_state = dut.state.value
#
#    while True:
#        await falling_edge #when module would change
#        await read_only
#        state = dut.state.value
#        sig = { 's00_tvalid':dut.s00_axis_tvalid.value,
#                's00_tready':dut.s00_axis_tready.value,
#                'm00_tvalid':dut.m00_axis_tvalid.value,
#                'm00_tready':dut.m00_axis_tready.value
#        }
#        #sts_sampling_function(states[state],sig)
#        sts_sampling_function(states[old_state],sig)
#        old_state = state


#
OS = coverage_section(
CoverPoint("top.os.s00_tvalid",
	    xf=lambda sig: sig.get('s00_tvalid'),
	    bins=['V:0->0','V:0->1','V:1->0','V:1->1']
	    ),
CoverPoint("top.os.s00_tready",
	    xf=lambda sig: sig.get('s00_tready'),
	    bins=['R:0->0','R:0->1','R:1->0','R:1->1']
	    ),
CoverPoint("top.os.m00_tvalid",
	    xf=lambda sig: sig.get('m00_tvalid'),
	    bins=['V:0->0','V:0->1','V:1->0','V:1->1']
	    ),
CoverPoint("top.os.m00_tready",
	    xf=lambda sig: sig.get('m00_tready'),
	    bins=['R:0->0','R:0->1','R:1->0','R:1->1']
	    ),
CoverCross("top.os.s_cross",
	    items=[ "top.os.s00_tvalid",
		    "top.os.s00_tready"],
	    ),
CoverCross("top.os.m_cross",
	    items=[ "top.os.m00_tvalid",
		    "top.os.m00_tready"],
	    )
)

@OS
def os_sampling_function(sig):
    pass

def get_rv(dut):
    return {'s00_tvalid':dut.s00_axis_tvalid.value,
	    's00_tready':dut.s00_axis_tready.value,
	    'm00_tvalid':dut.m00_axis_tvalid.value,
	    'm00_tready':dut.m00_axis_tready.value}

def match(old,new):
    outstr = ''
    if old:
	outstr+='1'
    else:
	outstr+='0'
    outstr += '->'
    if new:
	outstr+='1'
    else:
	outstr+='0'
    return outstr

async def os_monitor(dut):
    read_only = ReadOnly()
    falling_edge = FallingEdge(dut.s00_axis_aclk)
    rising_edge = RisingEdge(dut.s00_axis_aclk)
    await read_only
    olds = get_rv(dut)
    while True:
	await falling_edge #when module would change
	await read_only
	news = get_rv(dut)
	sig = {}
	for i in ['s00_tvalid','s00_tready','m00_tvalid','m00_tready']:
	    if 'v' in i:
		sig[i] = 'V:'+match(olds[i],news[i])
	    else:
		sig[i] = 'R:'+match(olds[i],news[i])
	os_sampling_function(sig)
	olds = news # remember for future compare

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
def axis_skid_buffer_model(val):
    sig_in.append(val)
    sig_out_exp.append(val)

@cocotb.test()
async def test_a(dut):
    """cocotb test for averager controller"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=axis_skid_buffer_model)
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

    #feed the driver on the M Side:
    for i in range(50):
	data = {'type':'write_single', "contents":{"data": random.randint(1,255),"last":0}}
	ind.append(data)
	pause = {"type":"pause","duration":random.randint(1,6)}
	ind.append(pause)
    ind.append({'type':'write_burst', "contents": {"data": np.array(list(range(100)))}})
    ind.append({'type':'pause','duration':2}) #end with pause
    #feed the driver on the S Side with on/off backpressure!
    for i in range(50):
	outd.append({'type':'read', "duration":random.randint(1,10)})
	outd.append({'type':'pause', "duration":random.randint(1,10)})
    await ClockCycles(dut.s00_axis_aclk, 500)

    
    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv('sim_result', "./"), 'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :/"

def axis_skid_buffer_runner():
    """Simulate the axis_skid_buffer using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sys.path.append(str(proj_path / "hdl" ))
    sources = [proj_path / "hdl" / "axis_skid_buffer.sv"]
    #sources = [proj_path / "hdl" / "j_math.sv"]
    build_test_args = ["-Wall"]
    parameters = {} #!!!
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    hdl_toplevel = "axis_skid_buffer"
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
   axis_skid_buffer_runner()


