#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class HolonomicBotController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.timer = self.create_timer(1.0, self.control_loop)
        self.x_goal = 0.0
        self.y_goal = 0.0
        self.theta_goal = 0.0
        self.kp_linear = 0.2
        self.kp_angular = 0.5
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]  # Example list of y-coordinates for goals
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0]  # Example list of theta for goals
        self.current_goal_index = 0
        self.goal_tolerance_x = 0.5  # Tolerance for goal in x-direction
        self.goal_tolerance_y = 0.5
        self.goal_tolerance_theta = 0.5# Tolerance for goal in y-direction

    def odometry_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])
        self.x = position.x
        self.y = position.y

    def control_loop(self):
        if self.current_goal_index < len(self.x_goals):
            self.x_goal = self.x_goals[self.current_goal_index]
            self.y_goal = self.y_goals[self.current_goal_index]
            self.theta_goal = self.theta_goals[self.current_goal_index]
            
            error_x = self.x_goal - self.x
            error_y = self.y_goal - self.y
            error_theta = self.theta_goal - self.theta
            print(f"errx{self.x} erry{self.y} theta:{error_theta}")
            
            linear_vel_x = self.kp_linear * error_x
            linear_vel_y = self.kp_linear * error_y
            angular_vel = self.kp_angular * error_theta

            twist = Twist()
            twist.linear.x = linear_vel_x
            twist.linear.y = linear_vel_y
            twist.angular.z= angular_vel

            self.publisher.publish(twist)

            # Check if the goal has been reached
            if abs(error_x) < self.goal_tolerance_x and abs(error_y) < self.goal_tolerance_y:
                # Stop the robot
                twist.linear.x = 0.0
                twist.linear.y = 0.0
                twist.angular.z = 0.0
                self.publisher.publish(twist)
                # Stabilize at the goal for a duration (e.g., 1 second)
            
    
    def next_goal(self):
        self.current_goal_index += 1  # Move to the next goal
        self.get_logger().info("Moving to the next goal.")

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class HolonomicBotController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.timer = self.create_timer(1.0, self.control_loop)
        self.x_goal = 0.0
        self.y_goal = 0.0
        self.theta_goal = 0.0
        self.kp_linear = 0.3
        self.kp_angular = 0.5
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]  # Example list of y-coordinates for goals
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0]  # Example list of theta for goals
        self.current_goal_index = 0
        self.goal_tolerance_x = 1  # Tolerance for goal in x-direction
        self.goal_tolerance_y = 1
        self.goal_tolerance_theta = 0.5  # Tolerance for goal in y-direction

    def odometry_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])
        self.x = position.x
        self.y = position.y

    def control_loop(self):
        if self.current_goal_index < len(self.x_goals):
            self.x_goal = self.x_goals[self.current_goal_index]
            self.y_goal = self.y_goals[self.current_goal_index]
            self.theta_goal = self.theta_goals[self.current_goal_index]

            error = math.sqrt((self.x_goal - self.x)**2 + (self.y_goal - self.y)**2)
            error_goal = math.atan2(self.y_goal -self.y,self.x_goal - self.x)
            error_theta = error_goal - self.theta
            print(f"err{error} x{self.x} y:{self.y} theta:{error_theta}")

            linear_vel_x = self.kp_linear * error
            linear_vel_y = self.kp_linear * error
            angular_vel = self.kp_angular * error_theta
            twist = Twist()
            
            twist.linear.x = linear_vel_x
            twist.linear.y = linear_vel_y
            
            if abs(error_goal) < self.goal_tolerance_theta:
                twist.angular.z = error_theta
                self.publisher.publish(twist)
                print("changing angle")
            elif (error) >= self.goal_tolerance_x:
                    twist.linear.x = linear_vel_x
                    twist.linear.y = linear_vel_y
                    self.publisher.publish(twist)
            else:
                if abs(error) < self.goal_tolerance_x or abs(error) < self.goal_tolerance_y:
                    # Stop the robot
                    twist.linear.x = 0.0
                    twist.linear.y = 0.0
                    self.publisher.publish(twist)
                    self.next_goal()

    def next_goal(self):
        self.current_goal_index += 1  # Move to the next goal
        self.get_logger().info("Moving to the next goal.")

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from my_robot_interfaces.srv import NextGoal
from tf_transformations import euler_from_quaternion
from nav_msgs.msg import Odometry
import math


class HBTask1BController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')

        # Initialize Publisher and Subscriber
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)

        # Declare a Twist message
        self.vel = Twist()

        # Initialize the required variables to 0
        self.x_d = 0
        self.y_d = 0
        self.theta_d = 0

        # For maintaining control loop rate.
        self.rate = self.create_rate(100)

        # Variables that may be needed for the control loop
        self.Kp_x = 0.5  # Adjust as needed
        self.Kp_y = 0.5  # Adjust as needed
        self.Kp_theta = 0.5 # Adjust as needed

        # Flag to track end of goal list
        self.flag = 0

        # Client for the "next_goal" service
        self.cli = self.create_client(NextGoal, 'next_goal')
        self.req = NextGoal.Request()
        self.index = 0

    def odometry_callback(self, msg):
        # Handle the Odometry message
        # Extract the robot's position and orientation information from the message
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation

        # Calculate the current position of the robot
        self.x = position.x
        self.y = position.y
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])

    """def send_request(self, index):
        self.req.request_goal = index
        self.future = self.cli.call_async(self.req)"""

def main(args=None):
        rclpy.init(args=args)

        # Create an instance of the HBTask1BController class
        ebot_controller = HBTask1BController()

        # Send an initial request with the index from ebot_controller.index
        ebot_controller.send_request(ebot_controller.index)

        # Main loop
        while rclpy.ok():
            # Check if the service call is done
            if ebot_controller.future.done():
                try:
                    # Response from the service call
                    response = ebot_controller.future.result()
                except Exception as e:
                    ebot_controller.get_logger().info('Service call failed %r' % (e,))
                else:
                    # Extract goal pose information from the service response
                    x_goal = response.x_goal
                    y_goal = response.y_goal
                    theta_goal = response.theta_goal
                    ebot_controller.flag = response.end_of_list

                    # Calculate error in global frame
                    error_x = x_goal - ebot_controller.x
                    error_y = y_goal - ebot_controller.y
                    error_theta = theta_goal - ebot_controller.theta

                    # Implement a P controller for velocity control
                    ebot_controller.vel.linear.x = ebot_controller.Kp_x * error_x
                    ebot_controller.vel.linear.y = ebot_controller.Kp_y * error_y
                    ebot_controller.vel.angular.z = ebot_controller.Kp_theta * error_theta

                    # Safety Check: Make sure the velocities are within a range
                    # You can add code here to limit the maximum velocities if necessary

                    # Publish the calculated velocity
                    ebot_controller.publisher.publish(ebot_controller.vel)

                    if ebot_controller.flag == 1:
                        ebot_controller.index = 0
                    ebot_controller.send_request(ebot_controller.index)

            # Spin once to process callbacks
            rclpy.spin_once(ebot_controller)

        # Destroy the node and shut down ROS
        ebot_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class HolonomicBotController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.timer = self.create_timer(1.0, self.control_loop)
        self.x_goal = 0.0
        self.y_goal = 0.0
        self.theta_goal = 0.0
        self.kp_linear = 0.3
        self.kp_angular = 0.5
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]  # Example list of y-coordinates for goals
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0]  # Example list of theta for goals
        self.current_goal_index = 0
        self.goal_tolerance_x = 1.7  # Tolerance for goal in x-direction
        self.goal_tolerance_y = 1
        self.goal_tolerance_theta = 0.5  # Tolerance for goal in y-direction

    def odometry_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])
        self.x = position.x
        self.y = position.y
        

    def control_loop(self):
        if self.current_goal_index < len(self.x_goals):
            self.x_goal = self.x_goals[self.current_goal_index]
            self.y_goal = self.y_goals[self.current_goal_index]
            self.theta_goal = self.theta_goals[self.current_goal_index]
            global error, error_goal, error_theta,twist
            error = math.sqrt((self.x_goal - self.x)**2 + (self.y_goal - self.y)**2)
            error_goal = math.atan2(self.y_goal -self.y,self.x_goal - self.x)
            error_theta = error_goal - self.theta
            print(f"x:{self.x} x_er{error}")

            linear_vel_x = self.kp_linear * error
            linear_vel_y = self.kp_linear * error
            angular_vel = self.kp_angular * error_theta
            twist = Twist()
            if (error_theta) > self.goal_tolerance_theta :
                twist.angular.z =  angular_vel
                self.publisher.publish(twist)
            elif error_theta < self.goal_tolerance_theta :
                twist.angular.z = 0.0
                self.publisher.publish(twist)
                if error >= self.goal_tolerance_x:
                    twist.linear.x = linear_vel_x 
                    twist.linear.y = linear_vel_y
                    self.publisher.publish(twist)
                elif error < self.goal_tolerance_x:
                    # Stop the robot
                    twist.linear.x = 0.0
                    twist.linear.y = 0.0
                    self.publisher.publish(twist)
                    self.next_goal()
        
    def next_goal(self):
        self.current_goal_index += 1
         
        self.get_logger().info("Moving to the next goal.")
        self.control_loop() 
        print("loop started")

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()
    
    
    #!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class HolonomicBotController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.timer = self.create_timer(1.0, self.control_loop)
        self.x_goal = 0.0
        self.y_goal = 0.0
        self.theta_goal = 0.0
        self.kp_linear = 0.3
        self.kp_angular = 0.5
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]  # Example list of y-coordinates for goals
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0]  # Example list of theta for goals
        self.current_goal_index = 0
        self.goal_tolerance_x = 1.5  # Tolerance for goal in x-direction
        self.goal_tolerance_y = 1
        self.goal_tolerance_theta = 0.1  # Tolerance for goal in y-direction

    def odometry_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])
        self.x = position.x
        self.y = position.y

    def move_to_goal(self):
        self.x_goal = self.x_goals[self.current_goal_index]
        self.y_goal = self.y_goals[self.current_goal_index]
        self.theta_goal = self.theta_goals[self.current_goal_index]
        global error, error_goal, error_theta, twist
        error = math.sqrt((self.x_goal - self.x)**2 + (self.y_goal - self.y)**2)
        error_goal = math.atan2(self.y_goal - self.y, self.x_goal - self.x)
        error_theta = error_goal - self.theta
        print(f"theta:{self.theta_goal} t_err{error_theta} x_err{error} gc {self.current_goal_index}")

        if abs(error_theta) > self.goal_tolerance_theta:
            # Rotate to the desired theta
            angular_vel = self.kp_angular * error_theta
            twist = Twist()
            twist.angular.z = angular_vel
            self.publisher.publish(twist)
        else:
            # When theta_goal is reached, switch to "move" state
            twist = Twist()
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            
        if error >= self.goal_tolerance_x:
            linear_vel_x = self.kp_linear * error
            linear_vel_y = self.kp_linear * error
            twist = Twist()
            twist.linear.x = linear_vel_x
            twist.linear.y = linear_vel_y
            self.publisher.publish(twist)
        else:
            self.next_goal()

        

    def control_loop(self):
        if self.current_goal_index < len(self.x_goals):
            self.move_to_goal()

    def next_goal(self):
        self.current_goal_index += 1
        self.get_logger().info("Moving to the next goal.")

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()




#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class HolonomicBotController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.timer = self.create_timer(1.0, self.control_loop)
        self.x_goal = 0.0
        self.y_goal = 0.0
        self.theta_goal = 0.0
        self.kp_linear = 0.3
        self.kp_angular = 0.5
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]  # Example list of y-coordinates for goals
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0]  # Example list of theta for goals
        self.current_goal_index = 0
        self.goal_tolerance_x = 0.6  # Tolerance for goal in x-direction
        self.goal_tolerance_y = 1
        self.goal_tolerance_theta = 0.1  # Tolerance for goal in y-direction

    def odometry_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])
        self.x = position.x
        self.y = position.y
        

    def control_loop(self):
        if self.current_goal_index < len(self.x_goals):
            self.x_goal = self.x_goals[self.current_goal_index]
            self.y_goal = self.y_goals[self.current_goal_index]
            self.theta_goal = self.theta_goals[self.current_goal_index]
            global error, error_goal, error_theta,twist
            
            error = math.sqrt((self.x_goal - self.x)**2 + (self.y_goal - self.y)**2)
            
            error_goal = math.atan2(self.y_goal -self.y,self.x_goal - self.x)
            
            error_theta = round((error_goal - self.theta),3)
            print(f"goal_t: {self.theta_goal}t_err:{error_theta} t:{self.theta}err:{error}")


            linear_vel_x = self.kp_linear * error
            linear_vel_y = self.kp_linear * error
            angular_vel = self.kp_angular * error_theta
            twist = Twist()
            
            if abs (error_theta) > self.goal_tolerance_theta :
                twist.angular.z =  angular_vel
            else:
                if error >= self.goal_tolerance_x:
                    twist.linear.x = linear_vel_x
                    twist.linear.y = linear_vel_y
                else:
                    twist.linear.x = 0.0
                    twist.linear.y = 0.0
                    self.next_goal()
                    
            self.publisher.publish(twist)
                    
                       
        
    def next_goal(self):
        self.current_goal_index += 1
        self.get_logger().info("Moving to the next goal.")
        self.control_loop() 

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()
    
    
    
    #crt code 
    #!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from tf_transformations import euler_from_quaternion

class HolonomicBotController(Node):

    def __init__(self):
        super().__init__('hb_task1b_controller')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odometry_callback,
            10)
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.timer = self.create_timer(1.0, self.control_loop)
        self.x_goal = 0.0
        self.y_goal = 0.0
        self.theta_goal = 0.0
        self.kp_linear = 0.3
        self.kp_angular = 0.5
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]  # Example list of y-coordinates for goals
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0]  # Example list of theta for goals
        self.current_goal_index = 0
        self.goal_tolerance_x = 0.6  # Tolerance for goal in x-direction
        self.goal_tolerance_y = 1
        self.goal_tolerance_theta = 0.1  # Tolerance for goal in y-direction

    def odometry_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        (_, _, self.theta) = euler_from_quaternion(
            [orientation.x, orientation.y, orientation.z, orientation.w])
        self.x = position.x
        self.y = position.y

    def control_loop(self):
        if self.current_goal_index < len(self.x_goals):
            self.x_goal = self.x_goals[self.current_goal_index]
            self.y_goal = self.y_goals[self.current_goal_index]
            self.theta_goal = self.theta_goals[self.current_goal_index]
            
            # Calculate the error in the global frame
            error_x_global = self.x_goal - self.x
            error_y_global = self.y_goal - self.y
            
            # Calculate the global angle error using atan2
            error_goal_global = math.atan2(error_y_global, error_x_global)
            
            # Update the robot's orientation to the goal orientation
            self.theta = self.theta_goal
            
            print(f"goal_t: {self.theta_goal} t_err: 0.0 t: {self.theta} err: {error_x_global}, {error_y_global}")

            twist = Twist()
            
            # Calculate linear velocities to reach the goal position
            linear_vel_x = self.kp_linear * error_x_global
            linear_vel_y = self.kp_linear * error_y_global
            twist.linear.x = linear_vel_x
            twist.linear.y = linear_vel_y
                
            # Check if both x and y errors are within their respective tolerances
            if abs(error_x_global) < self.goal_tolerance_x and abs(error_y_global) < self.goal_tolerance_y:
                self.next_goal()
                    
            self.publisher.publish(twist)

    def next_goal(self):
        self.current_goal_index += 1
        self.get_logger().info("Moving to the next goal.")
        self.control_loop() 

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()



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
        self.kp_linear = 0.1
        self.kp_angular = 0.5
        self.goal_tolerance_x = 0.1
        self.goal_tolerance_y =0.1
        self.goal_tolerance_theta = 0.1
        
        # Initialise the required variables to 0

        # For maintaining control loop rate.
        self.rate = self.create_rate(100)
        # Initialise variables that may be needed for the control loop
        # For ex: x_d, y_d, theta_d (in **meters** and **radians**) for defining desired goal-pose.
        # and also Kp values for the P Controller

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
                x_goal     = response.x_goal
                y_goal      = response.y_goal
                theta_goal  = response.theta_goal
                ebot_controller.flag = response.end_of_list
                ####################################################
                
                error_x_global = x_goal - ebot_controller.hb_x
                error_y_global = y_goal - ebot_controller.hb_y
                #error_goal_global = math.atan2(error_y_global, error_x_global)
                #error_theta = error_goal_global-theta_goal8 
            # Calculate the global angle error using atan2
            
                print(f"goal_x: {x_goal} y_goal:{y_goal} coor: {ebot_controller.hb_x}, {ebot_controller.hb_y} err{error_x_global}")

                twist = Twist()
                
            # Calculate linear velocities to reach the goal position
                linear_vel_x = ebot_controller.kp_linear * error_x_global
                linear_vel_y = ebot_controller.kp_linear * error_y_global
                twist.linear.x = linear_vel_x
                twist.linear.y = linear_vel_y
                
            # Check if both x and y errors are within their respective tolerances
                if abs(error_x_global) < ebot_controller.goal_tolerance_x and abs(error_y_global) < ebot_controller.goal_tolerance_y:
                    twist.linear.x = 0.0
                    twist.linear.y = 0.0
            
                ebot_controller.cmd_vel_publisher.publish(twist)
                ############     DO NOT MODIFY THIS       #########
                ebot_controller.index += 1
                if ebot_controller.flag == 1 :
                    ebot_controller.index = 0
                ebot_controller.send_request(ebot_controller.index)
                ####################################################

        # Spin once to process callbacks
        rclpy.spin_once(ebot_controller)
    
    # Destroy the node and shut down ROS
    ebot_controller.destroy_node()
    rclpy.shutdown()

    if __name__ == '__main__':
        main()