def bit_2_degree(bit_angle):
	return (360*bit_angle)/(2**16)

def degree_2_bit(real_angle):
	return (real_angle/360)*(2**16)

def pack_complex(angle,mag):
	return ((int(angle) & 0xFFFF) << 16) | (int(mag) & 0xFFFF)

def unpack_complex(packed):
    angle = (packed >> 16) & 0xFFFF
    magnitude = packed & 0xFFFF
    return angle, magnitude

print(bit_2_degree(32000))
print(degree_2_bit(180))

x=pack_complex(degree_2_bit(180),120)

print(x)
print(unpack_complex(x))
