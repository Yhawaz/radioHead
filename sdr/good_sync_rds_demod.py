#!/usr/bin/env python3

import numpy as np
from numpy.fft import fft
from scipy.signal import resample_poly, firwin, bilinear, lfilter
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import scipy
import rds_decode

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
x = np.fromfile('npr.raw', dtype=np.complex64)
sample_rate = 250e3

duration_s = len(x) / sample_rate
##print(f"Recording is {duration_s} s long.")

#  Demod
demoded_sig = 0.5 * np.angle(x[0:-1] * np.conj(x[1:]))
#demoded_sig = x

plot_fft_real(demoded_sig,250e3)

pilot_tone_bandpass = scipy.signal.firwin(numtaps = 501, cutoff = [16e3, 22e3], fs = sample_rate, pass_zero = "bandpass")
pilot_tone_extracted = scipy.signal.lfilter(pilot_tone_bandpass, [1.0], demoded_sig)

pilot_tone_zero_crossings_indices = np.where(np.diff(np.sign(pilot_tone_extracted)))[0]
pilot_tone_zero_crossings = np.zeros((len(pilot_tone_extracted,)), dtype = np.int8)
pilot_tone_zero_crossings[pilot_tone_zero_crossings_indices] = 1

pilot_tone_peak = np.max(pilot_tone_extracted)
pilot_tone_clipped = np.clip(pilot_tone_extracted, -pilot_tone_peak / 2, pilot_tone_peak / 2)

rds_carrier_bandpass = scipy.signal.firwin(numtaps = 501, cutoff = [57e3 - 3e3, 57e3 + 3e3], fs = sample_rate, pass_zero = "bandpass")
pilot_tone_tripled_extracted = scipy.signal.lfilter(rds_carrier_bandpass, [1.0], pilot_tone_clipped)

rds_signal = scipy.signal.lfilter(rds_carrier_bandpass, [1.0], demoded_sig)


synchronous_mixed = rds_signal * pilot_tone_tripled_extracted

lowpass = scipy.signal.firwin(numtaps = 501, cutoff = 3e3, fs = sample_rate)
lowpassed_synchronous_mixed = scipy.signal.lfilter(lowpass, [1.0], synchronous_mixed)
plt.plot(lowpassed_synchronous_mixed)
plt.show()

lowpassed_synchronous_mixed /= np.max(lowpassed_synchronous_mixed)

times = np.linspace(0, duration_s, len(lowpassed_synchronous_mixed))
#plt.plot(lowpassed_local_osc_mixed, label = "Local Osc Demod")
#plt.plot(times, lowpassed_synchronous_mixed, label = "Synchronous Demod")
#plt.plot(times, symbol_clock, label = "Symbol Clock")
plt.legend()
plt.show()

for counter_start in range(0, 32, 2):
    symbol_clock = np.zeros((len(pilot_tone_extracted),), dtype = np.uint8)
    counter = counter_start
    for i in range(len(pilot_tone_zero_crossings)):
        if pilot_tone_zero_crossings[i]:
            if counter % 32 == 0: # 16 samples per symbol, but there are 2 zero-crossings per cycle, so divide by 32.
                symbol_clock[i] = 1
            counter += 1
    if counter_start == 31:
        print(f"Average symbol clock frequency: {float(sum(symbol_clock.astype(np.uint32))) / duration_s} symbols/second")
    plt.plot(times, symbol_clock, '*')
    plt.show()

    bits = ((lowpassed_synchronous_mixed > 0)[symbol_clock == 1]).astype(np.uint8)
    rds_decode.rds_decode(bits)
    print("\033[1;31m~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\033[0m")
