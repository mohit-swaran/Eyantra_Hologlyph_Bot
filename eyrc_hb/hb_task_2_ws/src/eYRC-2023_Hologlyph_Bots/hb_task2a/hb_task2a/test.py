import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Pose2D
from geometry_msgs.msg import Wrench

class HBController(Node):
    def __init__(self):
        super().__init__('test_node')
        
        # Initialze Publisher and Subscriber
        # NOTE: You are strictly NOT-ALLOWED to use "cmd_vel" or "odom" topics in this task
        self.vel_left = self.create_publisher(Wrench,'/hb_bot_1/left_wheel_force',10)
        self.vel_right = self.create_publisher(Wrench,'/hb_bot_1/right_wheel_force',10)
        self.vel_rear = self.create_publisher(Wrench,'/hb_bot_1/rear_wheel_force',10)
        
    def inverse_kinematics(self,linear_x,linear_y,angular_z):
    
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
    hb_controller = HBController()
    
    linear_x = 15.0
    linear_y = 20.0
    angular_z = 0.0
                
    w1,w2,w3 = hb_controller.inverse_kinematics(linear_x,linear_y,angular_z)
    
    vel = Wrench()
    
    vel.force.y = w2
    hb_controller.vel_left.publish(vel)
    
    vel.force.y = w1
    hb_controller.vel_right.publish(vel)
    
    vel.force.y = w3
    hb_controller.vel_rear.publish(vel)
    
    rclpy.spin_once(hb_controller)

    hb_controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()