################### IMPORT MODULES #######################
import rclpy 
import cv2
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose2D
from cv_bridge import CvBridge
from rclpy.node import Node

# Import the required modules
##############################################################
class ArUcoDetector(Node):

    def __init__(self):
        super().__init__('ar_uco_detector')
        self.create_subscription(Image,"/camera/image_raw",self.image_callback)
        self.aruco_pub = self.create_publisher(Pose2D,"/detected_aruco",10)
        # Subscribe the topic /camera/image_raw
        self.cv_bridge =CvBridge


    def image_callback(self, msg):
        cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        #convert ROS image to opencv image
        detected_aruco= cv2.aruco.detectmarkers()
        #Detect Aruco marker
        self.aruco_pub(detected_aruco)
        # Publish the bot coordinates to the topic  /detected_aruco

def main(args=None):
    rclpy.init(args=args)

    aruco_detector = ArUcoDetector()

    rclpy.spin(aruco_detector)

    aruco_detector.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()