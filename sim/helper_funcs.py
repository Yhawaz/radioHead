import numpy as np
import scipy
from scipy.signal import firwin
from scipy.io import wavfile

#fighting with functions lmao

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

	imag = val & 0xFFFF
	real = (val >> 16)

	if(imag>(2**15)-1):
		imag=(2**16)-1-imag

	if(real>(2**15)-1):
		real=(2**16)-1-real

	real=np.int16(real)
	iamg=np.int16(imag)

	cur_val = real + 1j*imag 
	if last_val is None:
		#whatever we fail teh first idga
		demod_int = val
	else:
		demod_int = 0.5*np.angle(last_val*np.conj(cur_val)) 
	
	final_val = int(degree_2_bit(np.degrees(demod_int)))
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

prev_val = None

#this is gonna assume radians but whatever

angle1 =np.radians(325) #30 degrees
mag = 200

angle2 =np.radians(255) #30 degrees

imag1 = mag * np.sin(angle1)
imag2 = mag * np.sin(angle2)

real1 = mag * np.cos(angle1)
real2 = mag * np.cos(angle2)

complex1=pack_32bits(imag1,real1)
complex2=pack_32bits(imag2,real2)
print(complex1)
print(complex2)

get_angle_via_dot(complex1,complex2)


print(bit_2_degree(25858))
print(bit_2_degree(39678))
print("nya")

angle_bits=degree_2_bit(357)
prev_val=degree_2_bit(3)

cur_val =int(angle_bits) & 0xFFFF

demod_int = min(cur_val-prev_val,prev_val-cur_val)

demod_int = int(demod_int) & 0xFFFF
print(bit_2_degree(demod_int))

print(bit_2_degree(3889))
print(bit_2_degree(36656))

print(bit_2_degree(3936))
print(bit_2_degree(7870))

print(degree_2_bit(np.degrees(-np.pi)))

#audio testing

adc_sample_rate_hz = 64e6
carrier_frequency_hz = 5e6
fm_deviation_hz = 75e3
baseband_sample_rate_hz = 44_100

act_data = np.fromfile(r"../sdr/15khz_tone_at_5_mhz.raw").astype(np.complex64) / 30000 # undoing the scaling
print("nya")
n = np.arange(len(act_data))
mix = np.exp(-1j * 2 * np.pi * carrier_frequency_hz * n / adc_sample_rate_hz)
big_baseband = act_data * mix
half_big=int(.25*len(big_baseband))
baseband=big_baseband[0:half_big]
b, a = scipy.signal.butter(3, 3e5 / (0.5 * adc_sample_rate_hz))
dm_filtered = scipy.signal.lfilter(b, a, baseband)

real=dm_filtered.real.astype(np.int16)
imag=dm_filtered.imag.astype(np.int16)
complex_val=np.zeros(len(real),dtype=np.uint32)

for i in range(len(real)):
	python_model(complex_val[i])

phase_diff1 = np.angle(np.conj(dm_filtered[:-1]) * dm_filtered[1:])

audio_44k1 = scipy.signal.resample_poly(phase_diff1, baseband_sample_rate_hz, int(adc_sample_rate_hz),window=('kaiser', 8.6))

wavfile.write("coorect.wav", 44_100, audio_44k1)

audio_python = scipy.signal.resample_poly(phase_diff_python, baseband_sample_rate_hz, int(adc_sample_rate_hz),window=('kaiser', 8.6))

wavfile.write("python.wav", 44_100, audio_python)

