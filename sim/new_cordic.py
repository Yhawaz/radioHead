import sys
import math

#precompute
cordic_angles = [180/3.14159*math.atan(2**(-i)) for i in range(17)]
x = int(sys.argv[1])
y = int(sys.argv[2])
z = 30

exp_x = x * math.cos(30/180*3.14519)
exp_y = x * math.sin(30/180*3.14159)

#actual run-time:
for i in range(16):
    if z < 0: #sng(y)==1
        xn = x + 1/(2**i)*y
        yn = y - 1/(2**i)*x
        zn = z + cordic_angles[i]
    else:  #sng(y) == -1
        xn = x - 1/(2**i)*y
        yn = y + 1/(2**i)*x
        zn = z - cordic_angles[i]

    print(f"x:{xn}, y:{yn}, z:{zn}")
    x = xn
    y = yn
    z = zn

print(f"Actual angles x:{x/1.646}, y:{y/1.646}")
print(f"Expected angles x:{exp_x}, y:{exp_y}")
