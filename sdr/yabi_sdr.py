import numpy as np
from numpy.fft import fft
from scipy.signal import resample_poly, firwin, bilinear, lfilter
import matplotlib.pyplot as plt
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
x = np.fromfile('gqrx1.raw', dtype=np.complex64)
sample_rate = 250e3

#  Demod
demoded_sig = 0.5 * np.angle(x[0:-1] * np.conj(x[1:]))

plot_fft_real(demoded_sig,250e3)


pilot_tone_bandpass = scipy.signal.firwin(numtaps = 5001, cutoff = [17e3, 19e3], fs = sample_rate, pass_zero = "bandpass")
pilot_tone_extracted = scipy.signal.lfilter(pilot_tone_bandpass, [1.0], demoded_sig)

pilot_tone_peak = np.max(pilot_tone_extracted)
pilot_tone_clipped = np.clip(pilot_tone_extracted, -pilot_tone_peak / 2, pilot_tone_peak / 2)

rds_carrier_bandpass = scipy.signal.firwin(numtaps = 5001, cutoff = [57e3 - 1e3, 57e3 + 1e3], fs = sample_rate, pass_zero = "bandpass")
pilot_tone_tripled_extracted = scipy.signal.lfilter(rds_carrier_bandpass, [1.0], pilot_tone_clipped)

rds_signal = scipy.signal.lfilter(rds_carrier_bandpass, [1.0], demoded_sig)

mixed = rds_signal * pilot_tone_tripled_extracted

lowpass = scipy.signal.firwin(numtaps = 5001, cutoff = 2e3, fs = sample_rate)
lowpassed_mixed = scipy.signal.lfilter(lowpass, [1.0], mixed)

plt.plot(lowpassed_mixed)
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.title("Recovered BPSK Data")
plt.show()
