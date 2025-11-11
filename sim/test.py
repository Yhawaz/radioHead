def bit_2_degree(bit_angle):
	return (360*bit_angle)/(2**16)
def degree_2_bit(real_angle):
	return (real_angle/360)*(2**16)

print(bit_2_degree(32000))
print(degree_2_bit(180))
