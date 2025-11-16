import numpy as np
import scipy
from scipy.signal import firwin
from scipy.io import wavfile

#fighting with functions lmao

FIXED_SCALE= 32767.0 
fixed_point=1
#angle stuff
def bit_2_degree(bit_angle):
    return (360*bit_angle)/(2**16)

def degree_2_bit(real_angle):
    return (real_angle/360)*(2**16)

#this was named wrong, this just unapcks a high low
def unpack_32bits(packed):
    high = (packed >> 16) & 0xFFFF
    low = packed & 0xFFFF

	#im just using the dtype cause that makes my life easier it dosen't matter if the test cases are slow
  #  high = np.array([high], dtype=np.uint16).view(np.uint16)[0]
  #  low = np.array([low], dtype=np.uint16).view(np.uint16)[0]
    return high, low

def pack_32bits(high,low):
	return ((int(high*fixed_point) & 0xFFFF) << 16) | (int(low*fixed_point) & 0xFFFF)


def nunmpy_to32bit(complexy):
	return pack_32bits(np.real(complexy),np.imag(complexy))

#dealing with raw complex numbers
phase_diff_python=[]
phase_diff_verilog=[]

last_val= None
def python_model(val):
	global last_val
	global phase_diff_python

	real = val & 0xFFFF
	imag = (val >> 16)

	#did this because numpy kept getting overflow errors with 2s compliment so i just took it into my own hands
	if(imag>(2**15)-1):
		imag=imag-(2**16)-1

	if(real>(2**15)-1):
		real=real-(2**16)-1

	real=np.int16(real)
	imag=np.int16(imag)

	cur_val = real + 1j*imag 
	if last_val is None:
		#whatever we fail teh first idga
		demod_int = val
	else:
		demod_int = 0.5*np.angle(last_val*np.conj(cur_val)) 
	
	final_val = demod_int
	phase_diff_python.append(final_val)
	last_val = cur_val

def complex_bit_to_numpy(complexy):
	# assuming high is real, and low is imag

	imag,real = unpack_32bits(complexy)
	return np.complex128(np.real(real/fixed_point) + 1j*imag/fixed_point)

def get_angle_via_dot(packed_compa, packed_compb):
    complex_a = complex_bit_to_numpy(packed_compa)
    complex_b = complex_bit_to_numpy(packed_compb)

    vec_a = np.array([complex_a.real, complex_a.imag])
    vec_b = np.array([complex_b.real, complex_b.imag])
    
    print("ang decoded 1", np.degrees(np.angle(complex_a)))
    print("ang decoded 2", np.degrees(np.angle(complex_b)))
    
    cos_theta = np.dot(vec_a,vec_b) / (np.abs(complex_a) * np.abs(complex_b))
    
    diff = np.arccos(cos_theta)
    print("Angle difference (degrees):", np.degrees(diff))
    return diff
#audio testing
#commenting for oliver to read this
adc_sample_rate_hz = 64e6
carrier_frequency_hz = 5e6
fm_deviation_hz = 75e3
baseband_sample_rate_hz = 44_100

#yoink data
act_data = np.load(r"../sdr/quick_brown_fox_at_5_mhz_plusnoise.npy").astype(np.complex64)
print(act_data)


print("nya")
n = np.arange(len(act_data))

#mix it mix it mix it
mix = np.exp(-1j * 2 * np.pi * carrier_frequency_hz * n / adc_sample_rate_hz)
#only wokr with 1/4 so i dont wait a fucking hour
big_baseband = act_data * mix
half_big=int(.25*len(big_baseband))
baseband=big_baseband[0:half_big]
b, a = scipy.signal.butter(3, 3e5 / (0.5 * adc_sample_rate_hz))
dm_filtered = scipy.signal.lfilter(b, a, baseband)

#turn it into "bit data", just to emulate our cocotb model

real=dm_filtered.real.astype(np.int16)
imag=dm_filtered.imag.astype(np.int16)
complex_val=np.zeros(len(real),dtype=np.uint32)
print(real)
print(imag)

#now that we have that run it through what our python model is doing
for i in range(len(real)):
	python_model((imag[i].astype(np.int32) << 16) | (real[i].astype(np.uint32) & 0xFFFF))


#make da audio
audio_python = scipy.signal.resample_poly(phase_diff_python, baseband_sample_rate_hz, int(adc_sample_rate_hz),window=('kaiser', 8.6))

wavfile.write("python.wav", 44_100, audio_python)
#heres our right answer
phase_diff1 = np.angle(np.conj(dm_filtered[:-1]) * dm_filtered[1:])

audio_44k1 = scipy.signal.resample_poly(phase_diff1, baseband_sample_rate_hz, int(adc_sample_rate_hz),window=('kaiser', 8.6))

wavfile.write("coorect.wav", 44_100, audio_44k1)

