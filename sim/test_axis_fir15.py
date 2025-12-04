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
from scipy.signal import lfilter,lfiltic,firwin

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
    for i in range(len(coeffs)):
        for b in range(8):
            dut.coeffs[b+8*i].value = (coeffs[i]>>b)&0x1

def generate_signed_8bit_sine_waves(sample_rate, duration,frequencies, amplitudes):
    """
    frequencies (float): The frequency of the sine waves in Hz.
    relative amplitudes (float) of the sinewaves (0 to 1.0).
    sample_rate (int): The number of samples per second.
    duration (float): The duration of the time series in seconds.
    """
    num_samples = int(sample_rate * duration)
    time_points = np.arange(num_samples) / sample_rate
    # Generate a sine wave with amplitude 1.0
    result = np.zeros(num_samples, dtype=int)
    assert len(frequencies) == len(amplitudes), "frequencies must match amplitudes"
    for i in range(len(frequencies)):
        sine_wave = amplitudes[i]*np.sin(2 * np.pi * frequencies[i] * time_points)
        # Scale the sine wave to the 8-bit signed range [-128, 127]
        scaled_wave = sine_wave * 127
        # make 8bit signed integers:
        result+=scaled_wave.astype(np.int8)
    return (time_points,result)

sig_in = []
sig_out_exp = [] #contains list of expected outputs (Growing)
sig_out_act = [] #contains list of expected outputs (Growing)

# Coefficients for the test
#coeffs = [-2,-3,-4,0,9,21,32,36,32,21,9,0,-4,-3,-2]
#coeffs = [-3,14,-20,6,16,-5,-41,68,-41,-5,16,6,-20,14,-3]
#coeffs = [3,14,21,21,15,40,75,102,75,40,15,21,21,14,3]
# These coeffs are the ones that correspond to the line:
taps = firwin(numtaps=101, cutoff=6.25e3, fs=250e3)
max = np.max(abs(taps))
k = 127/max
coeffs = [round(k * tap) for tap in taps]
count = 0
initial = [0 for i in range(len(coeffs))]
expected = []
# Creaing the input data


# def j_math_model(val):
#     sig_in.append(val)
#     result = 3*val + 10000
#     sig_out_exp.append(result)


#(0th index is actual out, 1st delay array)
# elements from the output array are popped by the scoreboard

def model_fir_filter(sample):
    # you have to append one of the results to the sig out exp array
    global initial,count
    if count == 0:
        initial = [0 for i in range(len(coeffs)-1)]
    #print(f"This is initial:{initial} and {count}")
    a = lfilter(coeffs,[1.0],[sample],zi=initial)
    
    initial = a[1]

    good_data = int(a[0][0])
    expected.append(good_data)
    if(count > 0):
        # offset required
        sig_in.append(sample)
        sig_out_exp.append(expected[-2])
    else:
        # first two expected samples are zero
        sig_out_exp.append(0)
    count = count + 1

    
    

    




@cocotb.test()
async def test_a(dut):
    global initial,count
    """cocotb test for AXIS FIR 15 no backpressure"""
    inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=model_fir_filter)
    outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: sig_out_act.append(x))
    ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
    outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port
    # Create a scoreboard on the stream_out bus
    scoreboard = Scoreboard(dut,fail_immediately=False)
    scoreboard.add_interface(outm, sig_out_exp)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)

    # Set the coefficients
    #await drive_coeffs(dut,coeffs)

    # Generate the sine input data
    t,si = generate_signed_8bit_sine_waves(
    sample_rate=100e6,
    duration=100e-6,
    frequencies=[3e3,15e3,35e6, 50e6],
    amplitudes=[0.5,0.5,0.1, 0.7]
    )

    #(pts)
    #assert 1 == 2
    #feed the driver on the M Side:
    for i in range(len(t)):
        ind.append({'type':'write_single', "contents":{"data": int(si[i]),"last":0}})
        ind.append({"type":"pause","duration":10})
    ind.append({'type':'write_burst', "contents": {"data": si[0:99]}})
    ind.append({'type':'pause','duration':2}) #end with pause

    #feed the driver on the S Side:
    #always be ready to receive data:
    outd.append({'type':'read', "duration":10000000})

    #await ClockCycles(dut.s00_axis_aclk, 110*1000*2)
    await ClockCycles(dut.s00_axis_aclk, 200000)
    dut._log.info(f"In Transactions:{inm.transactions}, Out Transactions:{outm.transactions}")
    assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :-/ In: {inm.transactions}, Out: {outm.transactions}"
    fig, axs = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    
    # Plot each signal on its own axis
    axs[0].plot(t, sig_out_act[0:len(t)], label="Signal 1", color="r")
    axs[0].set_ylabel("Module Output")
    axs[0].legend()

    axs[2].plot(t, si, label="Signal 3", color="b")
    axs[2].set_ylabel("Input Signal")
    axs[2].set_xlabel("Time")
    axs[2].legend()

    plt.tight_layout()
    plt.show()
    print(f"sig_in \n {sig_in}")
    print(f"sig_out_exp \n {sig_out_exp}")
    print(f"sig_out_act \n {sig_out_act}")

# Resetting the global variables
count = 0
initial = [0 for i in range(14)]
expected = []
sig_in = []
sig_out_exp = [] #contains list of expected outputs (Growing)
sig_out_act = [] #contains list of expected outputs (Growing)

@cocotb.test()
async def test_b(dut):
   global initial,count
   """cocotb test for AXIS fir 15 with sporadic backpressure"""
   inm = AXIS_Monitor(dut,'s00',dut.s00_axis_aclk,callback=model_fir_filter)
   outm = AXIS_Monitor(dut,'m00',dut.s00_axis_aclk,callback=lambda x: sig_out_act.append(x))
   ind = M_AXIS_Driver(dut,'s00',dut.s00_axis_aclk) #M driver for S port
   outd = S_AXIS_Driver(dut,'m00',dut.s00_axis_aclk) #S driver for M port

   # Create a scoreboard on the stream_out bus
   scoreboard = Scoreboard(dut,fail_immediately=False)
   scoreboard.add_interface(outm, sig_out_exp)
   cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())
   await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)
   count = 0
   initial = [0 for i in range(14)]
   #await drive_coeffs(dut,coeffs)
# Generate the sine input data
   t,si = generate_signed_8bit_sine_waves(
   sample_rate=100e6,
   duration=100e-6,
   frequencies=[15e3,35e6, 50e6],
   amplitudes=[0.5,0.1, 0.7]
)

   #feed the driver on the M Side:
   for i in range(len(t)):
       data = {'type':'write_single', "contents":{"data": int(si[i]),"last":0}}
       ind.append(data)
       pause = {"type":"pause","duration":random.randint(1,6)}
       ind.append(pause)
   ind.append({'type':'write_burst', "contents": {"data": si[0:99]}})
   ind.append({'type':'pause','duration':2}) #end with pause
   #feed the driver on the S Side with on/off backpressure!
   for i in range(len(t)):
       outd.append({'type':'read', "duration":random.randint(1,10)})
       outd.append({'type':'pause', "duration":random.randint(1,10)})
   await ClockCycles(dut.s00_axis_aclk, len(t)*3)
   assert inm.transactions==outm.transactions, f"Transaction Count doesn't match! :-/ In: {inm.transactions}, Out: {outm.transactions}"

def fir_runner():
    """Simulate the AXIS FIR 15 using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sys.path.append(str(proj_path / "hdl" ))
    sources = [proj_path / "hdl" / "axis_fir_15.sv"]
    build_test_args = ["-Wall"]
    parameters = {} #!!!
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    hdl_toplevel = "axis_fir_15"
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
    fir_runner()
