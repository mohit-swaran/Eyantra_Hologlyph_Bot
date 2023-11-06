import numpy as np

linear_x= 1
linear_y = 1
angular_z =1
inverse_matrix = np.array([[-2,2.75,2],
                            [4, 0,2],
                        [-2,-2.75,2]])
c_speed = np.array([[linear_x],[linear_y],[angular_z]])
w_speed =np.dot(inverse_matrix,c_speed)
w1 = w_speed[0]
w2 = w_speed[1]
w3 = w_speed[2] 


print(c_speed,w1,w2,w3)
