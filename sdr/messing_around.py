import numpy as np
import scipy
from scipy.signal import firwin
from scipy.io import wavfile
import matplotlib.pyplot as plt


c_data=np.load("../sdr/iq_15kHz_amped_raw.npy")

print(c_data.dtype)

c_data=c_data[:100]
c_data=.5*np.angle(c_data[0:-1]*np.conj(c_data[1:]))
plt.plot(c_data.real)
plt.show()


