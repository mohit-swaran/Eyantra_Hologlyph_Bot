import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 
from geometry_msgs.msg import Pose2D

class ArUcoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  # Replace with your image topic
            self.image_callback,
            10
        )
        self.cv_bridge = CvBridge()
        self.aruco_pub = self.create_publisher(Pose2D, '/detected_aruco', 10)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters()

    def image_callback(self, msg):
        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error('Error converting ROS Image to OpenCV: %s' % str(e))
            return
        
        grayscale_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        _,threshold =cv2.threshold(grayscale_image, 127,255,cv2.THRESH_BINARY)
        # Detect ArUco markers
        corners, ids, _ = cv2.aruco.detectMarkers(threshold, self.aruco_dict, parameters=self.aruco_params)

        # If markers are found, you can iterate over them
        if ids is not None:
            for i in range(len(ids)):
                # Extract the ID of the ArUco marker
                id = ids[i]

                # Draw a rectangle and ArUco marker ID on the image
                cv2.aruco.drawDetectedMarkers(cv_image, corners,ids)
                print(ids)
                # Publish the detected ArUco ID as a Pose2D message
                pose_msg = Pose2D()

        # Display the CV image window with ArUco markers and IDs
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
 
