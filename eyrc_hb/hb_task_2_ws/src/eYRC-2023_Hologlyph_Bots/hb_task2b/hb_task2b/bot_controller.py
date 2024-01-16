#! /usr/bin/env python3

'''
*****************************************************************************************
*
*        		===============================================
*           		Hologlyph Bots (HB) Theme (eYRC 2023-24)
*        		===============================================
*
*  This script is to implement Task 2B of Hologlyph Bots (HB) Theme (eYRC 2023-24).
*  
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*
*****************************************************************************************
'''


# Team ID:		[ Team-ID ]
# Author List:		[ Names of team members worked on this file separated by Comma: Name1, Name2, ... ]
# Filename:		feedback.py
# Functions:
#			[ Comma separated list of functions in this file ]
# Nodes:		Add your publishing and subscribing node


################### IMPORT MODULES #######################

import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from geometry_msgs.msg import Wrench
from nav_msgs.msg import Odometry
import math
import time
from my_robot_interfaces.msg import Goal
from my_robot_interfaces.msg import Shape            

margin_tol_linear = 0.6

class HBController(Node):
    def __init__(self):
        super().__init__('hb_controller')
        

        # Initialise the required variables
        self.bot_1_index_x = 0
        self.bot_1_index_y = 0
        self.x_a=0
        self.y_a=0
        self.theta=0
        self.bot_1_x= []
        self.bot_1_y = []
        self.bot_1_theta = 0.0
        self.x = self.bot_1_x[self.bot_1_index_x]
        self.y = self.bot_1_y[self.bot_1_index_y]
        
        
        
        

        # Initialze Publisher and Subscriber
        # NOTE: You are strictly NOT-ALLOWED to use "cmd_vel" or "odom" topics in this task
	    #	Use the below given topics to generate motion for the robot.
        self.vel_left = self.create_publisher(Wrench,'/hb_bot_1/left_wheel_force',10)
        self.vel_right = self.create_publisher(Wrench,'/hb_bot_1/right_wheel_force',10)
        self.vel_rear = self.create_publisher(Wrench,'/hb_bot_1/rear_wheel_force',10)
	    #   /hb_bot_1/left_wheel_force,
	    #   /hb_bot_1/right_wheel_force,
	    #   /hb_bot_1/left_wheel_force,

        #Similar to this you can create subscribers for hb_bot_2 and hb_bot_3
        self.subscription = self.create_subscription(
            Goal,  
            'hb_bot_1/goal',  
            self.goalCallBack,  # Callback function to handle received messages
            10  # QoS profile, here it's 10 which means a buffer size of 10 messages
        )  

        self.pose_bot_1 = self.create_subscription(Pose2D,'/detected_aruco_1',self.aruco_pose,10)
        #self.pose_bot_2 = self.create_subscription(Pose2D,'/detected_aruco_2',10)
        #self.pose_bot_3 = self.create_subscription(Pose2D,'/detected_aruco_3',10)

        # For maintaining control loop rate.
        self.rate = self.create_rate(100)
         

    def inverse_kinematics(linear_x,linear_y,angular_z):
        ############ ADD YOUR CODE HERE ############
        inverse_matrix = np.array([[-2,2.75,2],
                                   [-2,-2.75,2],
                                   [4, 0,2]])
        c_speed = np.array([linear_x,linear_y,angular_z])
        w_speed =np.dot(inverse_matrix,c_speed)
        w1 = w_speed[0]
        w2 = w_speed[1]
        w3 = w_speed[2] 
        return w1, w2, w3
        # INSTRUCTIONS & HELP : 
        #	-> Use the target velocity you calculated for the robot in previous task, and
        #	Process it further to find what proportions of that effort should be given to 3 individuals wheels !!
        #	Publish the calculated efforts to actuate robot by applying force vectors on provided topics
        ############################################

    def goalCallBack(self, msg):
        self.bot_1_x = msg.x
        self.bot_1_y = msg.y
        self.bot_1_theta = msg.theta
        
    def aruco_pose(self,pose):
        self.x_a = pose.x
        self.y_a = pose.y
        self.theta = pose.theta

def main(args=None):
    rclpy.init(args=args)
    
    hb_controller = HBController()
       
    # Main loop
    while rclpy.ok():
        
        x_goal = hb_controller.x
        y_goal = hb_controller.y
        theta_goal = hb_controller.theta
        
        error_fb_x = x_goal - hb_controller.x_a
        error_fb_y = y_goal - hb_controller.y_a
        error_fb_theta = theta_goal - hb_controller.theta
        
        error_fb_x_l =[]
        error_fb_y_l =[]
        
        linear_x = hb_controller.kp * error_fb_x *6.9
        linear_y = hb_controller.kp * error_fb_y *6.9
        angular_z = hb_controller.kp_ang * error_fb_theta * 4.8
        
        w1,w2,w3 = hb_controller.inverse_kinematics(linear_x,linear_y,angular_z)
        
        vel = Wrench()
        
        vel.force.y = w1
        hb_controller.vel_left.publish(vel)
        vel.force.y = w2
        hb_controller.vel_right.publish(vel)
        vel.force.y = w3
        hb_controller.vel_rear.publish(vel)
        flag = 0
        if flag == len(hb_controller.x):
            plt.scatter()
        #if  abs(error_fb_x) < margin_tol_linear and abs(error_fb_y) < margin_tol_linear:
        time.sleep(2)
        hb_controller.bot_1_index_x +=1
        hb_controller.bot_1_index_y +=1
        error_fb_x_l.append(error_fb_x)
        error_fb_y_l.append(error_fb_y)
            
        # Spin once to process callbacks
        rclpy.spin_once(hb_controller)
    
    # Destroy the node and shut down ROS
    hb_controller.destroy_node()
    rclpy.shutdown()

# Entry point of the script
if __name__ == '__main__':
    main()
