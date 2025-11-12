import numpy as np
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
    high = np.array([high], dtype=np.uint16).view(np.int16)[0]
    low = np.array([low], dtype=np.uint16).view(np.int16)[0]

    return high, low

def pack_32bits(high,low):
	return ((int(high*fixed_point) & 0xFFFF) << 16) | (int(low*fixed_point) & 0xFFFF)

def nunmpy_to32bit(complexy):
	return pack_32bits(np.real(complexy),np.imag(complexy))

#dealing with raw complex numbers

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

angle1 =np.radians(215) #30 degrees
mag = 328.5

angle2 =np.radians(23) #30 degrees

imag1 = mag * np.sin(angle1)
imag2 = mag * np.sin(angle2)

real1 = mag * np.cos(angle1)
real2 = mag * np.cos(angle2)

complex1=pack_32bits(imag1,real1)
complex2=pack_32bits(imag2,real2)
print(complex1)
print(complex2)

get_angle_via_dot(complex1,complex2)

