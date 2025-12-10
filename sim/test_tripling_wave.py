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
    rst_val.value=0
    await Timer(30,"ns")
    rst_val.value=1
    await Timer(10,"ns")

@cocotb.test()
async def first_test(dut):
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start(start_high=False))
    dut.s00_axis_aresetn.value=1
    dut.s00_axis_tdata.value=0
    dut.s00_axis_tvalid.value=0
    received_messages = []
    await ClockCycles(dut.s00_axis_aclk,1)
    await drive_reset(dut.s00_axis_aresetn)
    #dut.clk_enable.value=1

    dut.s00_axis_tvalid.value=1


    #data
    proj_path = Path(__file__).resolve().parent.parent

    x = np.fromfile(str(proj_path) + '/sdr/' + 'hw_demoded_data.npy', dtype=np.int32)
    sample_rate = 250e3

    demoded_sig = x[33000:35000]
    triple_extracted_hw=np.zeros(len(demoded_sig))

    pilot_tone_bandpass = scipy.signal.firwin(numtaps = 501, cutoff = [16e3, 22e3], fs = sample_rate, pass_zero = "bandpass")
    pilot_tone_extracted_sw = scipy.signal.lfilter(pilot_tone_bandpass, [1.0], demoded_sig)
    
    
    for i in range(len(demoded_sig)):
        dut.s00_axis_tdata.value=int(demoded_sig[i])
        await ClockCycles(dut.s00_axis_aclk,1)
        if(dut.m00_axis_tvalid.value==1):
            triple_extracted_hw[i]=dut.m00_axis_tdata.value.signed_integer
        await ClockCycles(dut.s00_axis_aclk,1)

    print("NYAAA",np.max(triple_extracted_hw))
    
    t=np.arange(0,len(demoded_sig))
    fig,axs = plt.subplots(4,1,figsize=(8,8),sharex=True)
    plot_fft_real(triple_extracted_hw,250e3)
#
#    plt.plot(triple_extracted_hw,color="red")
#    plt.subplot()
#    plt.plot(pilot_tone_tripled_extracted)
#    plt.subplot()
#
#    fig, axs = plt.subplots(3, 1, figsize=(8, 8), sharex=True)

    try:
        # Plot each signal on its own axis
        axs[0].plot(t, triple_extracted_hw, label="Signal 1", color="r")
        axs[0].set_ylabel("hw tripled raw signal")
        axs[0].legend()

        axs[1].plot(t, pilot_tone_tripled_extracted, label="Signal 3", color="b")
        axs[1].set_ylabel("sw tripled signal")
        axs[1].set_xlabel("Time")
        axs[1].legend()

        plt.tight_layout()
        plt.show()
    except Exception as e:
        dut._log.info(f"Graphs were not printed because of the following error: {e}")
    
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
    sources = [proj_path / "hdl" / "fm32bit_19kHz_filter.v",
    proj_path / "hdl" / "fm32bit_57kHz_filter.v",
    proj_path / "hdl" / "Filter19.v",
    proj_path / "hdl" / "FilterCoef19.v",
    proj_path / "hdl" / "FilterTapSystolicPreAddWvlIn19.v",
    proj_path / "hdl" / "dsphdl_FIRFilter19.v",
    proj_path / "hdl" / "subFilter19.v",
    proj_path / "hdl" / "Filter19.v",
    proj_path / "hdl" / "FilterCoef19.v",
    proj_path / "hdl" / "FilterTapSystolicPreAddWvlIn19.v",
    proj_path / "hdl" / "dsphdl_FIRFilter19.v",
    proj_path / "hdl" / "triple.sv",
    proj_path / "hdl" / "triple_wave_maker.sv",
    proj_path / "hdl" / "subFilter19.v"] 
    #grow/modify this as needed.
    hdl_toplevel = "triple_wave_maker"
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

