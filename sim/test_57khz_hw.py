import cocotb
import os
import random
import sys
import logging
from pathlib import Path
from cocotb.triggers import Timer, ClockCycles, RisingEdge, FallingEdge, ReadOnly,with_timeout, First, Join, ReadWrite, Edge
from cocotb.clock import Clock
from cocotb.utils import get_sim_time as gst
#from cocotb.runner import get_runner
from vicoco.vivado_runner import get_runner
from cocotb.utils import get_sim_time

import numpy as np
from numpy.fft import fft
from scipy.signal import resample_poly, firwin, bilinear, lfilter
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import scipy
 
#cheap way to get the name of current file for runner:
test_file = os.path.basename(__file__).replace(".py","")

def plot_fft_real(real_signal, sample_rate, title = ""):
    fft = np.fft.fft(real_signal)
    fft = np.fft.fftshift(fft)
    freq_bins = np.linspace(-sample_rate / 2, sample_rate / 2, num = len(fft))
    plt.plot(freq_bins, np.log10(abs(fft)))
    plt.xlim(0, sample_rate / 2)
    plt.xlabel("Baseband Frequency [Hz]")
    plt.ylabel("Amplitude [dBFS]")
    plt.title(title)
    plt.show()

def generate_signed_32bit_sine_waves(sample_rate, duration,frequencies, amplitudes):
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
        scaled_wave = sine_wave * 32767
        # make 8bit signed integers:
        result+=scaled_wave.astype(np.int32)
    return (time_points,result)

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



async def drive_reset(rst_val):
    rst_val.value=1
    await Timer(30,"ns")
    rst_val.value=0
    await Timer(10,"ns")

@cocotb.test()
async def first_test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start(start_high=False))
    dut.reset.value=0
    dut.dataIn.value=0
    dut.clk_enable.value=1
    dut.validIn.value=0
    received_messages = []
    await ClockCycles(dut.clk,1)
    await drive_reset(dut.reset)
    #dut.clk_enable.value=1

    dut.validIn.value=1


    #data
    proj_path = Path(__file__).resolve().parent.parent

    x = np.fromfile(str(proj_path) + '/sdr/' + 'hw_demoded_data.npy', dtype=np.int32)
    sample_rate = 250e3

    demoded_sig = x[33000:35000]
    pilot_tone_extracted_hw=np.zeros(len(demoded_sig))

    pilot_tone_bandpass = scipy.signal.firwin(numtaps = 501, cutoff = [53e3, 60e3], fs = sample_rate, pass_zero = "bandpass")
    pilot_tone_extracted_sw = scipy.signal.lfilter(pilot_tone_bandpass, [1.0], demoded_sig)
    
    

    for i in range(len(demoded_sig)):
        if(i%1e3==0):
            print(i)
        dut.dataIn.value=int(demoded_sig[i])
        if(dut.validOut.value==1):
            pilot_tone_extracted_hw[i]=dut.dataOut.value.signed_integer>>30
        await ClockCycles(dut.clk,1)
    
    plot_fft_real(pilot_tone_extracted_hw,250e3)
    plot_fft_real(pilot_tone_extracted_sw,250e3)
    plt.plot(pilot_tone_extracted_hw)
    plt.plot(pilot_tone_extracted_sw)
    plt.show()
    
# boiler plate
"""the code below should largely remain unchanged in structure, though the specific files and things
specified should get updated for different simulations.
"""
def fm_filter_runner():
    """Simulate the fm_filter using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "vivado")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sources = [proj_path / "hdl" / "fm32bit_57kHz_filter.v",
    proj_path / "hdl" / "Filter57.v",
    proj_path / "hdl" / "FilterCoef57.v",
    proj_path / "hdl" / "FilterTapSystolicPreAddWvlIn57.v",
    proj_path / "hdl" / "dsphdl_FIRFilter57.v",
    proj_path / "hdl" / "subFilter57.v"] 
    #grow/modify this as needed.
    hdl_toplevel = "fm32bit_57kHz_filter"
    build_test_args = []
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

