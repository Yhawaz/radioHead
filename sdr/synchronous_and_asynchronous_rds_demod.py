#!/usr/bin/env python3

import numpy as np
from numpy.fft import fft
from scipy.signal import resample_poly, firwin, bilinear, lfilter
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import scipy

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

#yoink signal
x = np.fromfile("wmbr.raw", dtype=np.complex64)
sample_rate = 250e3

duration_s = len(x) / sample_rate
print(f"Recording is {duration_s} s long.")

#  Demod
demoded_sig = 0.5 * np.angle(x[0:-1] * np.conj(x[1:]))

plot_fft_real(demoded_sig,250e3)

pilot_tone_bandpass = scipy.signal.firwin(numtaps = 501, cutoff = [16e3, 22e3], fs = sample_rate, pass_zero = "bandpass")
pilot_tone_extracted = scipy.signal.lfilter(pilot_tone_bandpass, [1.0], demoded_sig)

pilot_tone_peak = np.max(pilot_tone_extracted)
pilot_tone_clipped = np.clip(pilot_tone_extracted, -pilot_tone_peak / 2, pilot_tone_peak / 2)

rds_carrier_bandpass = scipy.signal.firwin(numtaps = 501, cutoff = [57e3 - 3e3, 57e3 + 3e3], fs = sample_rate, pass_zero = "bandpass")
pilot_tone_tripled_extracted = scipy.signal.lfilter(rds_carrier_bandpass, [1.0], pilot_tone_clipped)

rds_signal = scipy.signal.lfilter(rds_carrier_bandpass, [1.0], demoded_sig)

nco_frequency = 57e3
nco_57_khz = np.cos(((2 * np.pi * nco_frequency) / sample_rate) * np.arange(len(demoded_sig)))
local_osc_mixed = rds_signal * nco_57_khz

synchronous_mixed = rds_signal * pilot_tone_tripled_extracted

lowpass = scipy.signal.firwin(numtaps = 501, cutoff = 3e3, fs = sample_rate)
lowpassed_local_osc_mixed = scipy.signal.lfilter(lowpass, [1.0], local_osc_mixed)
lowpassed_synchronous_mixed = scipy.signal.lfilter(lowpass, [1.0], synchronous_mixed)

lowpassed_local_osc_mixed /= np.max(lowpassed_local_osc_mixed)
lowpassed_synchronous_mixed /= np.max(lowpassed_synchronous_mixed)

fig, ax = plt.subplots()
times = np.linspace(0, duration_s, len(lowpassed_local_osc_mixed))
ax.plot(times, lowpassed_synchronous_mixed, label = "Synchronous Demod")
line, = ax.plot(times, lowpassed_local_osc_mixed, label = "Local Osc Demod")
ax.legend(loc = "upper right")

ax.set_xlabel("Time [s]")
ax.set_ylabel("Amplitude")
ax.set_title("Recovered BPSK Baseband (Use 'a' key to move NCO lower, 'd' key to move NCO higher in 0.01 Hz steps)")
fig.subplots_adjust(bottom = 0.25)
ax_slider = fig.add_axes([0.25, 0.1, 0.65, 0.03])
nco_freq_slider = Slider(
        ax = ax_slider,
        label = "NCO Frequency (kHz)",
        valmin = 57e3 - 10,
        valmax = 57e3 + 10,
        valinit = 57e3
)

def update(val):
    nco_57_khz = np.cos(((2 * np.pi * nco_freq_slider.val) / sample_rate) * np.arange(len(demoded_sig)))
    local_osc_mixed = rds_signal * nco_57_khz
    lowpassed_local_osc_mixed = scipy.signal.lfilter(lowpass, [1.0], local_osc_mixed)
    lowpassed_local_osc_mixed /= np.max(lowpassed_local_osc_mixed)
    line.set_ydata(lowpassed_local_osc_mixed)
    fig.canvas.draw_idle()

def on_press(event):
    if event.key == 'a':
        nco_freq_slider.set_val(nco_freq_slider.val - 0.01)
    elif event.key == 'd':
        nco_freq_slider.set_val(nco_freq_slider.val + 0.01)

fig.canvas.mpl_connect("key_press_event", on_press)
nco_freq_slider.on_changed(update)

#plt.legend()
plt.show()
