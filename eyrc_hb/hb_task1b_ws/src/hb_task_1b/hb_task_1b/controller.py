import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time
import math
from tf_transformations import euler_from_quaternion
from my_robot_interfaces.srv import NextGoal

class HBTask1BController(Node):

   def __init__(self):
        super().__init__('hb_task1b_controller')
        
        # Initialze Publisher and Subscriber
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_subscription = self.create_subscription(Odometry, '/odom', self.odometryCb, 10)
        # We'll leave this for you to figure out the syntax for
        # initialising publisher and subscriber of cmd_vel and odom respectively

        # Declare a Twist message
        self.hb_x= 0
        self.hb_y =0
        self.hb_theta =0
        self.kp_linear = 0.5
        self.kp_angular = 0.5
        self.goal_tolerance_x = 0.5
        self.goal_tolerance_y =0.5
        self.goal_tolerance_theta = 0.1
        
        self.rate = self.create_rate(100)

        # client for the "next_goal" service
        self.cli = self.create_client(NextGoal, 'next_goal')
        while not self.cli.wait_for_service(timeout_sec=1.0):
             self.get_logger().warn('Service not available or not initaited') 
        self.req = NextGoal.Request() 
        self.index = 0
        self.current_goal_index = 0
        
   def odometryCb(self, msg):
        # Extract pose data from Odometry message
        orientation = msg.pose.pose.orientation
        (roll, pitch, yaw) = euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])

        self.hb_x = msg.pose.pose.position.x
        self.hb_y = msg.pose.pose.position.y
        self.hb_theta = yaw
             
   def send_request(self,index):
        self.req.request_goal = self.index
        self.future = self.cli.call_async(self.req)
        
def main(args=None):
    rclpy.init(args=args)
    
    # Create an instance of the EbotController class
    ebot_controller = HBTask1BController()
   
    # Send an initial request with the index from ebot_controller.index
    ebot_controller.send_request(ebot_controller.index)
    
    # Main loop
    while rclpy.ok():

        # Check if the service call is done
        if ebot_controller.future.done():
            try:
                # response from the service call
                response = ebot_controller.future.result()
            except Exception as e:
                ebot_controller.get_logger().info(
                    'Service call failed %r' % (e,))
            else:
                #########           GOAL POSE             #########
                x_d     = response.x_goal 
                y_d      = response.y_goal 
                theta_d  = response.theta_goal 
                ebot_controller.flag = response.end_of_list
                ####################################################
                error_x_global = x_d - ebot_controller.hb_x
                error_y_global = y_d - ebot_controller.hb_y
                error_theta_global = theta_d - ebot_controller.hb_theta

                twist = Twist()
                
            # Calculate linear velocities to reach the goal position
                linear_vel_x = ebot_controller.kp_linear * error_x_global * 6
                linear_vel_y = ebot_controller.kp_linear * error_y_global * 6
                angular_vel_z = ebot_controller.kp_angular * error_theta_global * 6
                twist.linear.x = linear_vel_x
                twist.linear.y = linear_vel_y
                twist.angular.z = angular_vel_z
                print(error_x_global ,error_x_global)
                
            # Checking if both x and y errors are within their respective tolerances
                if abs(error_x_global) < ebot_controller.goal_tolerance_x and abs(error_y_global) < ebot_controller.goal_tolerance_y:
                    twist.linear.x = 0.0
                    twist.linear.y = 0.0
                    ebot_controller.cmd_vel_publisher.publish(twist)
                    if abs(error_theta_global) > ebot_controller.goal_tolerance_theta :
                        twist.angular.z= 0.0
                    ebot_controller.cmd_vel_publisher.publish(twist)
                    ebot_controller.index += 1
                    if ebot_controller.flag == 1 :
                        ebot_controller.index = 0
                    ebot_controller.send_request(ebot_controller.index)
                    
                ebot_controller.cmd_vel_publisher.publish(twist)
                
        # Spin once to process callbacks
        rclpy.spin_once(ebot_controller)
    
    # Destroy the node and shut down ROS
    ebot_controller.destroy_node()
    rclpy.shutdown()

    if __name__ == '__main__':
        main()