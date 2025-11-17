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
#from vicoco.vivado_runner import get_runner

from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.scoreboard import Scoreboard
import numpy as np
#import matplotlib.pyplot as plt
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



def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val   

exp = []
phi = 45
phi_rad = 45*np.pi/180

def model_cordic(sample):
    global exp
    # x is lower 15
    x = twos_comp(sample & 0xFFFF,16)

    I = np.cos(phi_rad)*x
    Q = np.sin(phi_rad)*x
    # Adding to all the arrays
    sig_in.append(sample)

    bit_I = round(I)
    bit_Q = round(Q)

    sig_out_exp.append((bit_I << 16) | (bit_Q)) # cos(angle) is in upper bits
    exp.append((I,Q))



@cocotb.test()
async def test_a(dut):
    global initial,count,phi
    """cocotb test for CORDIC"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=model_cordic)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: sig_out_act.append(x))
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port
    # Create a scoreboard on the stream_out bus
    scoreboard = Scoreboard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)


    # making the input data
    inputs = []
    x_vals = []
    y_vals = []
    act_list = []
    samples = 100
    dut.phi_in.value = phi

    angle_epsilon = 0.1
    magnitude_epsilon = 3
    for i in range(samples):

        # Test for all positive numbers
        # x = random.getrandbits(15)
        # y = random.getrandbits(15)
        # x_vals.append(x)
        # y_vals.append(y)

        x = random.getrandbits(16)
        y = 0
        x_vals.append(twos_comp(x,16))
        y_vals.append(0)

        # x is lower 15 and y is upper 15
        bin_val = format(y, f'0{16}b') + format(x, f'0{16}b')
        #print(f"bin: {bin_val},{len(bin_val)}")
        inputs.append(int(bin_val,2))
        #dut._log.info(f"Sending x:{twos_comp(x,16)} and y:{twos_comp(y,16)} as {int(bin_val,2)}")

    #(pts)
    #assert 1 == 2
    #feed the driver on the M Side:
    for i in range(samples):
        ind.append({'type':'write_single', "contents":{"data": inputs[i],"last":0}})
        ind.append({"type":"pause","duration":10})
    ind.append({'type':'write_burst', "contents": {"data": inputs}})
    samples = 2*samples
    ind.append({'type':'pause','duration':2}) #end with pause

    #feed the driver on the S Side:
    #always be ready to receive data:
    outd.append({'type':'read', "duration":samples})

    #await ClockCycles(dut.s00_axis_aclk, 110*1000*2)
    await ClockCycles(dut.s00_axis_aclk, 17*samples)
    dut._log.info(f"In Transactions:{inm.transactions}, Out Transactions:{outm.transactions}")
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :-/ In: {inm.transactions}, Out: {outm.transactions}"

    for sig in sig_out_act:
        #print(f"angle: {(sig & 0xFFFF0000) >> 16},ang: {(sig & 0xFFFF)/2**16*2*np.pi}")
        #print(f"mag:{(sig & 0xFFFF)}, ang:{ ((sig & 0xFFFF0000)>>16)/(2**16)*360}")
        mag = sig & 0xFFFF
        ang = ((sig & 0xFFFF0000)>>16)/(2**16)*360
        act_list.append((mag,ang))

    # Since the angles and magnitudes are not exactly the same, the lists will be iterated through and verified.
    # side stepping the score board
    for i in range(samples):
        act = act_list[i]
        act_mag = act[0]
        act_ang = act[1]

        expexcted = exp[i]
        exp_mag = expexcted[0]
        exp_ang = expexcted[1]

        assert abs(act_ang - exp_ang) < angle_epsilon, f"Oops. It seems the angle was wrong. Expected:{exp_ang}, Actual:{act_ang}"
        assert abs(act_mag - exp_mag) < magnitude_epsilon, f"Oops. It seems the magnitude was wrong. Expected:{exp_mag}, Actual:{act_mag}"
    dut._log.info(f"Successfully verified {samples} sample(s)!")

def cordic_runner():
    """Simulate the AXIS FIR 15 using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    
    sim = os.getenv("SIM", "icarus")
    #sim = os.getenv("SIM", "vivado")

    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sys.path.append(str(proj_path / "hdl" ))
    sources = [proj_path / "hdl" / "TRIG_cordic.sv"]
    build_test_args = ["-Wall"]
    parameters = {} #!!!
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    hdl_toplevel = "TRIG_cordic"
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
    cordic_runner()
