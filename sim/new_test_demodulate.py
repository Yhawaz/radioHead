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
import scipy

from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.scoreboard import Scoreboard
import numpy as np

from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db, coverage_section
import constraint
test_file = os.path.basename(__file__).replace(".py","")

#sometimes letting go is part of getting better

#victory over my past self 

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
    high = np.array([high], dtype=np.uint16).view(np.int16)[0]
    low = np.array([low], dtype=np.uint16).view(np.int16)[0]

    return high, low

def pack_32bits(high,low):
	return ((int(high*fixed_point) & 0xFFFF) << 16) | (int(low*fixed_point) & 0xFFFF)

class MeowBoard(Scoreboard):
    def compare(self, got, exp, log, strict_type=True):
        # Compare the types
        correct = abs(got-exp)<50

        strict_type=False

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
                thing = dict(data=data.signed_integer,last=last,
                             name=self.name,count=self.transactions)
                self.dut._log.info(f"{self.name}: {thing}")
                self._recv(data.integer)

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
sig_out_act = [] #contains list of expected outputs (Growing)

prev_val = None

def demodulate_model(val):
	
	global prev_val
	sig_in.append(val)

	imag = val & 0xFFFF
	real =(val >> 16)

	if(imag>(2**15)-1):
		imag=(2**16)-1-imag

	if(real>(2**15)-1):
		real=(2**16)-1-real

	real=np.int16(real)
	iamg=np.int16(imag)

	cur_val = real + 1j*imag 
	if prev_val is None:
		#whatever we fail teh first idga
		demod_int = val
	else:
		demod_int = 0.5*np.angle(prev_val*np.conj(cur_val)) 
	
	final_val = int(degree_2_bit(np.degrees(demod_int)))
	sig_out_exp.append(final_val)
	prev_val = cur_val

@cocotb.test()
async def test_a(dut):
    """cocotb test for averager controller"""
    global sig_out_act
    global sig_out_exp

    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=demodulate_model)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: sig_out_act.append(x))
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port

    # Create a scoreboard on the stream_out bus
    scoreboard = MeowBoard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())

    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)

    for i in range(100):
        rand_complex_num = random.randint(1,(2**32)-1)
        data = {'type':'write_single', "contents":{"data": rand_complex_num,"last":0}}
        ind.append(data)
        pause = {"type":"pause","duration":random.randint(1,6)}
        ind.append(pause)

    for i in range(200):
        outd.append({'type':'read', "duration":random.randint(1,10)})
        outd.append({'type':'pause', "duration":random.randint(1,10)})
    await ClockCycles(dut.s00_axis_aclk, 700)

    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :/"
    print("HEY",scoreboard.errors)
    assert scoreboard.errors == 0

#bad audio gen

phase_diff_python=[]
phase_diff_verilog=[]

last_val= None
def python_model(val):
	global last_val
	global phase_diff_python
	sig_in.append(val)

	imag = val & 0xFFFF
	real = (val >> 16)

	if(imag>(2**15)-1):
		imag=(2**16)-1-imag

	if(real>(2**15)-1):
		real=(2**16)-1-real

	real=np.int16(real)
	iamg=np.int16(imag)

	cur_val = real + 1j*imag 
	if last_val is None:
		#whatever we fail teh first idga
		demod_int = val
	else:
		demod_int = 0.5*np.angle(last_val*np.conj(cur_val)) 
	
	final_val = int(degree_2_bit(np.degrees(demod_int)))
	phase_diff_verilog.append(final_val)
	last_val = cur_val

@cocotb.test()
async def test_b(dut):
	global phase_diff_python
	global phase_diff_verilog

	inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback = python_model)
	outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: phase_diff_verilog.append(x))

	ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
	outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port
	#lets get those damn inputs ready

	proj_path = Path(__file__).resolve().parent.parent

	audio_data= str(proj_path) + "/sdr/" + "quick_brown_fox_at_5_mhz_plusnoise.npy"

	#big woke and their hard coded constants
	
	adc_sample_rate_hz = 64e6
	carrier_frequency_hz = 5e6
	fm_deviation_hz = 75e3
	baseband_sample_rate_hz = 44_100

	act_data = np.load(audio_data).astype(np.complex64) / 30000 # undoing the scaling
	n = np.arange(len(act_data))
	mix = np.exp(-1j * 2 * np.pi * carrier_frequency_hz * n / adc_sample_rate_hz)
	baseband = act_data * mix
	b, a = scipy.signal.butter(3, 3e5 / (0.5 * adc_sample_rate_hz))
	dm_filtered = scipy.signal.lfilter(b, a, baseband)
	real=dm_filtered.real.astype(np.int16)
	imag=dm_filtered.imag.astype(np.int16)
	complex_val=np.zeros(len(real),dtype=np.uint32)
	

	for i in range(len(real)):
		complex_val[i]=(real[i].astype(np.int32) << 16) | (imag[i].astype(np.uint32) & 0xFFFF)

	for i in range(len(real)):
		data = {'type':'write_single', "contents":{"data": complex_val[i],"last":0}}
		ind.append(data)
		pause = {"type":"pause","duration":random.randint(1,6)}
		ind.append(pause)
	for i in range(len(real)):
		outd.append({'type':'read', "duration":random.randint(10,20)})
		outd.append({'type':'pause', "duration":random.randint(1,10)})
	await ClockCycles(dut.s00_axis_aclk, len(real)*1.5)
	
	audio_verilog = scipy.signal.resample_poly(phase_diff_verilog, baseband_sample_rate_hz, int(adc_sample_rate_hz),window=('kaiser', 8.6))
	wavfile.write("verilog.wav", 44_100, audio_verilog)

	audio_python = scipy.signal.resample_poly(phase_diff_python, baseband_sample_rate_hz, int(adc_sample_rate_hz),window=('kaiser', 8.6))
	wavfile.write("verilog.wav", 44_100, audio_python)


def demodulate_runner():
    """Simulate the demodulate using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sys.path.append(str(proj_path / "hdl" ))
    sources = [ proj_path / "hdl" / "demo_shim.sv",proj_path / "hdl" / "demodulate.sv",proj_path / "hdl" / "cordic.sv"]
    build_test_args = ["-Wall"]
    parameters = {} #!!!
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    hdl_toplevel = "demo_shim"
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
