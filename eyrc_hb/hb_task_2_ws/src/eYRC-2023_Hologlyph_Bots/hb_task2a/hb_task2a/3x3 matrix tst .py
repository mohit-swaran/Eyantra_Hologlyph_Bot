import numpy as np 

inverse_matrix = np.array([[-0.33,0.58,0.33],
                                   [-0.33,-0.58,0.33],
                                   [0.67, 0,0.33]])
c_speed = np.array([-50,50,0])
w_speed =np.dot(inverse_matrix,c_speed)
w1 = w_speed[0]
w2 = w_speed[1]
w3 = w_speed[2] 
print(w1,w2,w3)