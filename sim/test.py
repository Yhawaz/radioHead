import numpy as np
#fighting with functions lmao


#angle stuff
def bit_2_degree(bit_angle):
    return (360*bit_angle)/(2**16)

def degree_2_bit(real_angle):
        return (real_angle/360)*(2**16)

def unpack_complex(packed):
    angle = (packed >> 16) & 0xFFFF
    magnitude = packed & 0xFFFF
    return angle, magnitude

prev_val = None

def demodulate_model(val):
    global prev_val
    sig_in.append(val)
    if(prev_val!=None):
        demod = 0.5 * np.angle(prev_val * np.conj(val))
        print(demod)
    else:
        demod = 0 

def pack_complex(angle,mag):
	return ((int(angle) & 0xFFFF) << 16) | (int(mag) & 0xFFFF)

def unpack_complex(packed):
    angle = (packed >> 16) & 0xFFFF
    magnitude = packed & 0xFFFF
    return angle, magnitude

def numpy_prac(compa,compb):
    maga=np.abs(compa)    
    magb=np.abs(compb)    
    print(maga)
    print(magb)

prev_val = None

def demodulate_model(val):
    global prev_val
    cur_angle = unpack_complex(val)[0]
    max=(2**16)-1
    angl_1=max(prev_val,val)
    angl_2=min(prev_val,val)
    if(prev_val is not None):
        if(prev_val != val):
            if(max-angl_1<angl_1):
                demod=(360-angl_1)+angl_2
            else:
                demod=angl_1-angle_2
        else:
            demod = 0
    else:
        demod = 0 
    prev_val = val
    print(demod)

x=pack_complex(degree_2_bit(180),120)
y=pack_complex(degree_2_bit(329),170)
new_x=unpack_complex(x)
newer_x=unpack_complex[1]

numpy_prac(x,y)

