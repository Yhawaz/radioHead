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

from scapy.utils import hexdump, hexdiff

from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.scoreboard import Scoreboard
import numpy as np

from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db, coverage_section
import constraint
test_file = os.path.basename(__file__).replace(".py","")

#helper funcs

fixed_point=1
def bit_2_degree(bit_angle):
    return (360*bit_angle)/(2**16)

def degree_2_bit(real_angle):
        return (real_angle/360)*(2**16)

#this was named wrong, this just unapcks a high low
def unpack_32bits(packed):
    high = (packed >> 16) & 0xFFFF
    low = packed & 0xFFFF

	#im just using the dtype cause that makes my life easier it dosen't matter if the test cases are slow
    high = np.array([high], dtype=np.uint16).view(np.uint16)[0]
    low = np.array([low], dtype=np.uint16).view(np.uint16)[0]

    return high, low

def pack_32bits(high,low):
	return ((int(high*fixed_point) & 0xFFFF) << 16) | (int(low*fixed_point) & 0xFFFF)
#dealing with raw complex numbers

def complex_bit_to_numpy(complexy):
	# assuming high is real, and low is imag
	imag,real = unpack_32bits(complexy)
	return np.complex128(np.real(real/fixed_point) + 1j*imag/fixed_point)

class MeowBoard(Scoreboard):
    def compare(self, got, exp, log, strict_type=True):
        # Compare the types
        correct = abs(got-exp)<200
        if strict_type and type(got) != type(exp):
            self.errors += 1
            log.error("Received transaction type is different than expected")
            log.info("Received: %s but expected %s" % (str(type(got)), str(type(exp))))
            if self._imm:
                assert False, (
                    "Received transaction of wrong type. "
                    "Set strict_type=False to avoid this."
                )
            return
        # Or convert to a string before comparison
        elif not strict_type:
            got, exp = str(got), str(exp)

        # Compare directly
        if not correct:
            self.errors += 1

            # Try our best to print out something useful
            #strgot, strexp = str(degree_2_bit(got)), str(degree_2_bit(exp))
            strgot, strexp = str(got), str(exp)

            log.error("Received transaction differed from expected output")
            if not strict_type:
                log.info("Expected:\n" + hexdump(strexp, dump=True))
            else:
                log.info("Expected:\n" + repr(exp))
            if not isinstance(exp, str):
                try:
                    for word in exp:
                        log.info(str(word))
                except Exception:
                    pass
            if not strict_type:
                log.info("Received:\n" + hexdump(strgot, dump=True))
            else:
                log.info("Received:\n" + repr(got))
            if not isinstance(got, str):
                try:
                    for word in got:
                        log.info(str(word))
                except Exception:
                    pass
            log.warning("Difference:")
            # NOTE: scapy.utils.hexdiff doesn't return a string but prints!
            hexdiff(strexp, strgot)
            if self._imm:
                assert False, "Received transaction differed from expected transaction"
        else:
            # Don't want to fail the test
            # if we're passed something without __len__
            try:
                log.debug("Received expected transaction %d bytes" % (len(got)))
                log.debug(repr(got))
            except Exception:
                pass


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
                thing = dict(data=data.integer,last=last,
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


prev_val = None
def demodulate_model(val):
	global prev_val
    
	angle_bits, mag_bits = unpack_32bits(val)
	angle_rad = np.radians(bit_2_degree(angle_bits))
    
	mag = 200 
	real = mag * np.cos(angle_rad)
	imag = mag * np.sin(angle_rad)
    
    
	if prev_val is None:
		demod_int = int(angle_bits) & 0xFFFF
	else:
		cur_val =int(angle_bits) & 0xffff

		demod_int = cur_val-prev_val
		
		half_pi = (2**15)-1
		twopi = (2**16)-1
		
		demod_int=demod_int + twopi
		if(demod_int > half_pi):
			demod_int=demod_int-half_pi 
		elif (demod_int<half_pi):
			demod_int=demod_int+half_pi

			demod_int = int(demod_int) & 0xffff

	sig_out_exp.append(int(demod_int))
	prev_val = angle_bits  # Store as complex for next comparison

@cocotb.test()
async def test_a(dut):
    """cocotb test for averager controller"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=demodulate_model)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk)
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port

    # Create a scoreboard on the stream_out bus
    scoreboard = MeowBoard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())

    #cocotb.start_soon(state_monitor(dut)) #feel free to bring back in
    #cocotb.start_soon(state_and_input_monitor(dut)) #feel free to bring back in
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)
    magnitude=random.randint(1,(2**16)-1)
    angle_bits=degree_2_bit(357)
    angle_bits2=degree_2_bit(3)
    numby1=pack_32bits(angle_bits,magnitude)
    numby2=pack_32bits(angle_bits2,magnitude)
    data = {'type':'write_single', "contents":{"data": numby2,"last":0}}
    ind.append(data)
    data = {'type':'write_single', "contents":{"data": numby1,"last":0}}
    ind.append(data)


    for i in range(500):
        angle = random.randint(1,(2**16)-1)
        magnitude=random.randint(1,(2**16)-1)
        numby=pack_32bits(angle,magnitude)
        data = {'type':'write_single', "contents":{"data": numby,"last":0}}
        ind.append(data)
        pause = {"type":"pause","duration":random.randint(1,6)}
        ind.append(pause)

    for i in range(60):
        outd.append({'type':'read', "duration":random.randint(1,10)})
        outd.append({'type':'pause', "duration":random.randint(1,10)})
    await ClockCycles(dut.s00_axis_aclk, 5000)

    
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :/"
    print("HEY",scoreboard.errors)
    assert scoreboard.errors == 0


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




