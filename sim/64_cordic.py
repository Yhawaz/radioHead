import sys
import math




circular = 1
linear = 0
hyperbolic = -1



def ROM_lookup(iteration, coordinate):
    if (coordinate == circular):
        return math.degrees(math.atan(2**(-1*iteration)))
    elif (coordinate == linear):
        return 2**(-1*iteration)
    elif (coordinate == hyperbolic):
        return (math.atanh(2**(-1*iteration)))



def rotation_mode(x, y, z, coordinate, iterations):
    a = 0.607252935;   # = 1/K
    
    x_val_list = []
    y_val_list = []
    z_val_list = []
    iterations_list = []

    i = 0;                  # Keeps count on number of iterations
    
    current_x = x         # Value of X on ith iteration 
    current_y = y         # Value of Y on ith iteration
    current_z = z         # Value of Z on ith iteration
    
    di = 0
    
    if (coordinate == hyperbolic):
        i = 1
    else:
        i = 0
        
    flag = 0
    
    if (iterations > 0):
        while (i < iterations):
            if (current_z < 0):
                di = -1
            else:
                di = +1
            next_z = current_z - di * ROM_lookup(i, coordinate)
            next_x = current_x - coordinate * di * current_y * (2**(-1*i))
            next_y = current_y + di * current_x * 2**(-1*i)
            
            current_x = next_x
            current_y = next_y
            current_z = next_z

            x_val_list.append(current_x)
            y_val_list.append(current_y)
            z_val_list.append(current_z)
            
            iterations_list.append(i)
            
            if (coordinate == hyperbolic):
                if ((i != 4) & (i != 13) & (i!=40)):
                    i = i+1
                elif (flag == 0):
                    flag = 1
                elif (flag == 1):
                    flag = 0
                    i = i+1
            else:
                i = i+1
    return { 'x':x_val_list, 'y':y_val_list, 'z':z_val_list, 'iteration':iterations_list, }



#precompute
cordic_angles = [180/3.14159*math.atan(2**(-i)) for i in range(17)]
x = int(sys.argv[1])
y = int(sys.argv[2])
z = 0

print(f"Correct result: {rotation_mode(x,y,z,circular,17)["z"]}")

flipped = False

if x < 0:
    flipped = True
    x = -x
    y = -x

#actual run-time:
for i in range(16):
    if y >0: #sng(y)==1
        xn = x + 1/(2**i)*y
        yn = y - 1/(2**i)*x
        zn = z - cordic_angles[i]
    else:  #sng(y) == -1
        xn = x - 1/(2**i)*y
        yn = y + 1/(2**i)*x
        zn = z + cordic_angles[i]

    print(f"x:{xn}, y:{yn}, z:{zn}")
    x = xn
    y = yn
    z = zn

print(x/1.646)
if flipped:
    print(-z - 180)
else:
    print(-z)
