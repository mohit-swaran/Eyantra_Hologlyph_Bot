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
        self.at_goal = False

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

            twist = Twist()

            # Calculate linear velocities to reach the goal position
            linear_vel_x = self.kp_linear * error_x_global
            linear_vel_y = self.kp_linear * error_y_global
            twist.linear.x = linear_vel_x
            twist.linear.y = linear_vel_y

            if (
                abs(error_x_global) < self.goal_tolerance_x
                and abs(error_y_global) < self.goal_tolerance_y
            ):
                # The robot is at the goal, update the orientation
                self.theta = math.atan2(math.sin(self.theta_goal - self.theta), math.cos(self.theta_goal - self.theta))
                self.at_goal = True
                self.get_logger().info("Reached the goal, waiting for orientation stabilization.")
            else:
                # Robot is not at the goal, move to the goal
                self.at_goal = False

            # Set the angular velocity to align with the goal orientation
            angular_error = self.theta_goal - self.theta
            twist.angular.z = self.kp_angular * angular_error

            # Print error in theta and goal theta
            self.get_logger().info(f"Error Theta: {angular_error}, Goal Theta: {self.theta_goal}")

            self.publisher.publish(twist)

            if self.at_goal and abs(angular_error) < self.goal_tolerance_theta:
                self.next_goal()

    def next_goal(self):
        self.current_goal_index += 1
        if self.current_goal_index >= len(self.x_goals):
            self.current_goal_index = 0  # Go back to the first goal
        self.get_logger().info("Moving to the next goal.")
        self.at_goal = False

def main(args=None):
    rclpy.init(args=args)
    controller = HolonomicBotController()
    rclpy.spin(controller)
    controller.destroy_node()
    rclpy.shutdown()

if you want to run this code you can use this command
```bash
ros2 run package_name python_file.py
