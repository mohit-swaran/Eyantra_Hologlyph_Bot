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
        self.odom_sub =self.create_subscription(Odometry,'hb_bot_1/odom_pose',self.odometryCb,2)
    
    
    def odometryCb(self, msg):
        # Extract pose data from Odometry message
        orientation = msg.pose.pose.orientation
        (roll, pitch, yaw) = euler_from_quaternion([orientation.x, orientation.y, orientation.z, orientation.w])

        self.hb_x = msg.pose.pose.position.x
        self.hb_y = msg.pose.pose.position.y
        self.hb_theta = yaw
        #print(f"x:{self.hb_x} y:{self.hb_y}")
    
def main(args=None):
        rclpy.init(args=args)
        
        holo_c = HBController()
        
        twist =Wrench()
        vel_r = 20.0
        vel_l = 20.0
        vel_rr= 20.0
        twist.force.y = vel_r
        holo_c.vel_right.publish(twist)
        print(f"right:{twist.force.y}")
        twist.force.y = vel_l
        holo_c.vel_left.publish(twist)
        print(f"left:{twist.force.y}")
        twist.force.y = vel_rr
        holo_c.vel_rear.publish(twist)
        print(f"rear:{twist.force.y}")
        
        
        rclpy.spin(holo_c)
        holo_c.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()
        