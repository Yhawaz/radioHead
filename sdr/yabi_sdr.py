import numpy as np
from numpy.fft import fft
from scipy.signal import resample_poly, firwin, bilinear, lfilter
import matplotlib.pyplot as plt

#yoink signal
x = np.fromfile('fm_rds_250k_1Msamples.iq', dtype=np.complex64)
sample_rate = 250e3
center_freq = 99.5e6

#  Demod
x = 0.5 * np.angle(x[0:-1] * np.conj(x[1:])) 
rawr=x

# grab 19khz tone

N = len(x)
f_o = -19e3 # amount we need to shift by
t = np.arange(N)/sample_rate # time vector
x = x * np.exp(2j*np.pi*f_o*t) # down shift

# Low-Pass Filter
taps = firwin(numtaps=101, cutoff=7.5e3, fs=sample_rate)
x = np.convolve(x, taps, 'valid')

x = x[::10]
fs = 25e3

#
fft_data=np.fft.fftshift((fft(rawr)))

#me struggling to plot a fft
plt.plot(fft_data*fft_data)
plt.show()
