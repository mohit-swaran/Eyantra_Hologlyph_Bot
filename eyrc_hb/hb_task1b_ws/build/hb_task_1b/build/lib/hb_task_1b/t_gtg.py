import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import sys
import math

class Turtle_GTG(Node):
    def __init__(self):
        super().__init__("Go_to_Goal_Node")
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.timer = self.create_timer(0.1, self.go_to_goal)
        self.pose = Pose()
        self.x_goals = [4, -4, -4, 4, 0]  # Example list of x-coordinates for goals
        self.y_goals = [4, 4, -4, -4, 0]
        self.theta_goals = [0, math.pi/2, math.pi, -math.pi/2, 0] 
        self.current_goal_index = 0
    def pose_callback(self, data):
        self.pose = data

    def go_to_goal(self):
        goal = Pose()
        if self.current_goal_index < len(self.x_goals):
            self.x_goal = self.x_goals[self.current_goal_index]
            self.y_goal = self.y_goals[self.current_goal_index]
            self.theta_goal = self.theta_goals[self.current_goal_index]

        new_vel = Twist()

        # Ecludian Distance
        distance_to_goal = math.sqrt( (self.x_goal - self.pose.x)**2  + (self.y_goal - self.pose.y)**2 )
        # Angle to Goal
        angle_to_goal =math.atan2(self.y_goal - self.pose.y , self.x_goal - self.pose.x)

        distance_tolerance = 0.1
        angle_tolerance = 0.01

        angle_error = angle_to_goal - self.pose.theta
        kp = 10

        if abs(angle_error) > angle_tolerance:
            new_vel.angular.z = kp * angle_error
        else :
            if( distance_to_goal ) >= distance_tolerance:
                new_vel.linear.x = kp * distance_to_goal
            else :
                new_vel.linear.x= 0.0
                self.get_logger().info("Goal Reached ")
                quit()


        self.cmd_vel_pub.publish(new_vel)
        self.current_goal_index +=1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = Turtle_GTG()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()