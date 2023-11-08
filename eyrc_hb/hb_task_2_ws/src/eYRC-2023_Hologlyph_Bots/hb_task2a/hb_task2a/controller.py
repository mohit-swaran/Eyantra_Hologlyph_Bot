#! /usr/bin/env python3

'''
*****************************************************************************************
*
*        		===============================================
*           		Hologlyph Bots (HB) Theme (eYRC 2023-24)
*        		===============================================
*
*  This script is to implement Task 2A of Hologlyph Bots (HB) Theme (eYRC 2023-24).
*  
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*
*****************************************************************************************
'''


# Team ID:		[HB-1476]
# Author List:		[Mohit.K,Puran.Y]
# Filename:		controller
# Functions:
#			[Send_request,aruco_detector,inverse_kinematics,main]
# Nodes:		[vel_left,vel_right,vel_rear,pose_sub]


################### IMPORT MODULES #######################

import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from geometry_msgs.msg import Wrench
from nav_msgs.msg import Odometry
import math
import time
from my_robot_interfaces.srv import NextGoal
# You can add more if required
##############################################################


# Initialize Global variables
margin_tol_linear = 0.6
x_values = []
y_values = []

################# ADD UTILITY FUNCTIONS HERE #################

##############################################################


# Define the HBController class, which is a ROS node
class HBController(Node):
    def __init__(self):
        super().__init__('hb_controller')
        
        # Initialze Publisher and Subscriber
        # NOTE: You are strictly NOT-ALLOWED to use "cmd_vel" or "odom" topics in this task
        self.vel_left = self.create_publisher(Wrench,'/hb_bot_1/left_wheel_force',10)
        self.vel_right = self.create_publisher(Wrench,'/hb_bot_1/right_wheel_force',10)
        self.vel_rear = self.create_publisher(Wrench,'/hb_bot_1/rear_wheel_force',10)
        self.pose_sub = self.create_subscription(Pose2D,"/detected_aruco",self.aruco_pose,10)
	 #	Use the below given topics to generate motion for the robot.
	    #   /hb_bot_1/left_wheel_force,
	    #   /hb_bot_1/right_wheel_force,
	    #   /hb_bot_1/left_wheel_force,

        self.x_a = 0
        self.y_a = 0
        self.theta = 0
        self.kp= 0.5
        self.kp_ang =1.0
        # For maintaining control loop rate.
        self.rate = self.create_rate(100)


        # client for the "next_goal" service
        self.cli = self.create_client(NextGoal, 'next_goal')      
        self.req = NextGoal.Request() 
        self.index = 0

    
    # Method to create a request to the "next_goal" service
    def send_request(self, request_goal):
        self.req.request_goal = request_goal
        self.future = self.cli.call_async(self.req)
    

    def aruco_pose(self,pose):
        self.x_a = pose.x
        self.y_a = pose.y
        self.theta = pose.theta 

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
    # Create an instance of the HBController class
    hb_controller = HBController()
   
    # Send an initial request with the index from ebot_controller.index
    hb_controller.send_request(hb_controller.index)
    print("Starting")
    # Main loop
    while rclpy.ok():

        # Check if the service call is done
        if hb_controller.future.done():
            try:
                # response from the service call
                response = hb_controller.future.result()
            except Exception as e:
                hb_controller.get_logger().info(
                    'Service call failed %r' % (e,))
            else:
                #########           GOAL POSE             #########
                x_goal      = response.x_goal + 250
                y_goal      = response.y_goal + 250
                theta_goal  = response.theta_goal
                hb_controller.flag = response.end_of_list
                ####################################################
                # Calculate Error from feedback
                theta_goal = np.arctan2(x_goal,y_goal)
                
                error_fb_x = x_goal - hb_controller.x_a
                error_fb_y = y_goal - hb_controller.y_a
                error_fb_theta = theta_goal - hb_controller.theta
                
                linear_x = hb_controller.kp * error_fb_x *6.9
                linear_y = hb_controller.kp * error_fb_y *6.9
                angular_z = hb_controller.kp_ang * error_fb_theta * 4.8
                
                # Change the frame by using Rotation Matrix (If you find it required)
                w1,w2,w3 = hb_controller.inverse_kinematics(linear_x,linear_y,angular_z)

                #print(f'x{error_fb_x},y{error_fb_y},th{error_fb_theta}')
                #print(f"dist{d}")
                #print(linear_x,linear_y,angular_z)
                # Calculate the required velocity of bot for the next iteration(s)
                
                # Find the required force vectors for individual wheels from it.(Inverse Kinematics)
               
                vel = Wrench()
                if abs(w1) > 120.0 or abs(w2) > 130.0 or abs(w3) > 120.0 :
                    w1=w1/3
                    w2=w2/3   
                    w3=w3/3 
                """elif abs(w1) < 20.0 or abs(w2) < 20.0 or abs(w3) < 20.0 :
                    w1=w1*10
                    w2=w2*10
                    w3=w3*10"""

                vel.force.y = w1
                hb_controller.vel_left.publish(vel)
                
                vel.force.y = w2
                hb_controller.vel_right.publish(vel)
                
                vel.force.y = w3
                hb_controller.vel_rear.publish(vel)
                    
                # Apply appropriate force vectors
                # Modify the condition to Switch to Next goal (given position in pixels instead of meters 
                    
                if  abs(error_fb_x) < margin_tol_linear and abs(error_fb_y) < margin_tol_linear:
                    
                    """x_values.append(hb_controller.x_a)
                    y_values.append(hb_controller.y_a)"""
                    
                    #print(f"Goal{hb_controller.index} completed!")
                    ############     DO NOT MODIFY THIS       #########
                    hb_controller.index += 1
                    if hb_controller.flag == 1 :
                        """plt.scatter(x_values,y_values)
                        print(f"x:{x_values}    y:{y_values}")
                        plt.show()"""
                        hb_controller.index = 0
                    hb_controller.send_request(hb_controller.index)
            ####################################################
                               
        # Spin once to process callbacks
        rclpy.spin_once(hb_controller)
    
    # Destroy the node and shut down ROS
    hb_controller.destroy_node()
    rclpy.shutdown()

# Entry point of the script
if __name__ == '__main__':
    main()