import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Wrench
from nav_msgs.msg import Odometry
import time
import math
from tf_transformations import euler_from_quaternion
from my_robot_interfaces.srv import NextGoal  

class HBController(Node):
    def __init__(self):
        super().__init__('wheel_test')
        
        # Initialze Publisher and Subscriber
        # NOTE: You are strictly NOT-ALLOWED to use "cmd_vel" or "odom" topics in this task
        self.vel_left = self.create_publisher(Wrench,'/hb_bot_1/left_wheel_force',10)
        self.vel_right = self.create_publisher(Wrench,'/hb_bot_1/right_wheel_force',10)
        self.vel_rear = self.create_publisher(Wrench,'/hb_bot_1/rear_wheel_force',10)
    
    
    def inverse_kinematics(self,linear_x,linear_y,angular_z):
        ############ ADD YOUR CODE HERE ############

        # INSTRUCTIONS & HELP : 
        #	-> Use the target velocity you calculated for the robot in previous task, and
        #	Process it further to find what proportions of that effort should be given to 3 individuals wheels !!
        #	Publish the calculated efforts to actuate robot by applying force vectors on provided topics
        ############################################
        inverse_matrix = np.array([[-2,2.75,2],
                                   [-2,-2.75,2],
                                   [4, 0,2]])
        c_speed = np.array([linear_x,linear_y,angular_z])
        w_speed =np.dot(inverse_matrix,c_speed)
        w1 = w_speed[0]
        w2 = w_speed[1]
        w3 = w_speed[2] 
        return w1, w2, w3
    
def main(args=None):
        rclpy.init(args=args)
        
        holo_c = HBController()
        
        twist =Wrench()
        linear_x = -50.0
        linear_y= 50.0
        angular_z = 0.0
        #w1,w2,w3 = holo_c.inverse_kinematics(linear_x,linear_y,angular_z)
        
        #print(holo_c.c_speed, w1,w2,w3)
        
        twist.force.y = 10.0
        holo_c.vel_left.publish(twist)
        print(f"left:{twist.force.y}")
        
        twist.force.y = 10.0
        holo_c.vel_right.publish(twist)
        print(f"right:{twist.force.y}")
        
        twist.force.y = 10.0
        holo_c.vel_rear.publish(twist)
        print(f"rear:{twist.force.y}")
        
        
        rclpy.spin(holo_c)