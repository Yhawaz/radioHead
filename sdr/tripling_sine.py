import numpy as np
import matplotlib.pyplot as plt
pilot_tone_amplitude=.1
pilot_tone_freq=19e3
sample_rate=250e3

pilot_tone = pilot_tone_amplitude * np.cos(((2 * np.pi * pilot_tone_freq) / sample_rate) * np.arange(500))
plt.plot(pilot_tone)
plt.show()
