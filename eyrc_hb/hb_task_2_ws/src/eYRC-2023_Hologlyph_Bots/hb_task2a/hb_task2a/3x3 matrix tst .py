import numpy as np 

w_vel = np.array([
            [-0.33, 0.58, 0.33],
            [-0.33, -0.58, 0.33],
            [0.67, 0.0, 0.33]
        ]) 
 
v_x = w_vel[1:3,0]
v_y = w_vel[:,1]
v_theta = w_vel[:,2]    
print(v_x)