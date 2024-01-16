import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Pose2D

# Default Camera Matrix (for illustrative purposes, replace with actual calibration)
cameraMatrix = np.array([[1000, 0, 320],
                         [0, 1000, 240],
                         [0, 0, 1]])

# Default Distortion Coefficients (for illustrative purposes, replace with actual calibration)
distCoeffs = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

class ArUcoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')
        self.bottom_left = None
        self.top_left = None
        self.top_right = None
        self.bottom_right = None

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  # Replace with your image topic
            self.image_callback,
            10
        )
        self.cv_bridge = CvBridge()
        self.pose_pub = self.create_publisher(Pose2D, '/detected_aruco', 10)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters()

    def image_callback(self, msg):
        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error('Error converting ROS Image to OpenCV: %s' % str(e))
            return

        _, threshold = cv2.threshold(cv_image, 127, 255, cv2.THRESH_BINARY)
        corners, ids, _ = cv2.aruco.detectMarkers(threshold, self.aruco_dict, parameters=self.aruco_params)

        if ids is not None:
            for i in range(len(ids)):
                id = ids[i]
                marker_corners = corners[i][0]
                center_x = int(np.mean(marker_corners[:, 0]))
                center_y = int(np.mean(marker_corners[:, 1]))
                cv2.circle(cv_image, (center_x, center_y), radius=4, color=(0, 0, 255), thickness=-1)
                cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)

                if id in [4, 8, 10, 12]:
                    if id == 4:
                        self.bottom_left = marker_corners[0]
                    elif id == 8:
                        self.top_left = marker_corners[1]
                    elif id == 10:
                        self.top_right = marker_corners[2]
                    elif id == 12:
                        self.bottom_right = marker_corners[3]

        cv2.imshow('ProcessedImage', cv_image)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    aruco_detector = ArUcoDetector()
    try:
        rclpy.spin(aruco_detector)
    except KeyboardInterrupt:
        pass

    aruco_detector.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
