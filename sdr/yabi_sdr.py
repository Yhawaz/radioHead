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
demoded_sig=x

# bandpass
taps = firwin(numtaps=101, cutoff=[17e3,21e3], fs=sample_rate,pass_zero=False)
x = np.convolve(x, taps, 'valid')

#tripled 
triple=[]
for val in x:
    triple.append(val**3)

band_pass_taps = firwin(numtaps=101, cutoff=[55e3,59e3], fs=sample_rate,pass_zero=False)
triple = np.convolve(triple, band_pass_taps, 'valid')


#fix it

orig_57=np.convolve(demoded_sig, band_pass_taps, 'valid')

#mixed_down_57=orig_57*triple
print(len(orig_57))
print(len(triple))

orig_57=orig_57[:len(triple)]
mixed_down=orig_57*triple

val_to_fft= orig_57 

low_pass_taps = firwin(numtaps=501, cutoff=2e3, fs=sample_rate)
mixed_down=np.convolve(mixed_down,low_pass_taps,'valid')
plt.plot(mixed_down)
plt.show()

#fft plotting i like
num_samples=len(val_to_fft)
fft_time=np.fft.rfft(val_to_fft)

freqs=np.fft.rfftfreq(num_samples,d=1/sample_rate)
plt.plot(freqs,fft_time*fft_time)
plt.show()

