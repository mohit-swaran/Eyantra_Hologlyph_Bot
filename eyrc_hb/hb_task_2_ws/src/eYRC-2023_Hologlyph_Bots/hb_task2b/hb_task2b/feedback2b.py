import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import Pose2D

cameraMatrix = np.array([[1000, 0, 320],
                         [0, 1000, 240],
                         [0, 0, 1]])
distCoeffs = np.array([0.0, 0.0, 0.0, 0.0, 0.0])

class ArUcoDetector(Node):
    def __init__(self):
        super().__init__('feedback2b')
        self.path_aruco1 = []
        self.path_aruco2 = []
        self.path_aruco3 = []
        # Initialize previous position to None
        self.prev_aruco1_position = None
        self.prev_aruco2_position = None
        self.prev_aruco3_position = None
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',  # Replace with your image topic
            self.image_callback,
            10
        )
        self.cv_bridge = CvBridge()
        
        self.pose_b1 = self.create_publisher(Pose2D, '/detected_aruco_1', 10)
        self.pose_b2 = self.create_publisher(Pose2D, '/detected_aruco_2', 10)
        self.pose_b3 = self.create_publisher(Pose2D, '/detected_aruco_3', 10)
        
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
        self.aruco_params = cv2.aruco.DetectorParameters()
        
    def image_callback(self, msg):
        try:
            self.cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error('Error converting ROS Image to OpenCV: %s' % str(e))
            return

        _, threshold = cv2.threshold(self.cv_image, 127, 255, cv2.THRESH_BINARY)
        corners, ids, _ = cv2.aruco.detectMarkers(threshold, self.aruco_dict, parameters=self.aruco_params)

        if ids is not None:
            for i in range(len(ids)):
                id = ids[i]
                marker_corners = corners[i][0]
                center_x = int(np.mean(marker_corners[:, 0]))
                center_y = int(np.mean(marker_corners[:, 1]))
                cv2.circle(self.cv_image, (center_x, center_y), radius=4, color=(0, 0, 255), thickness=-1)
                cv2.aruco.drawDetectedMarkers(self.cv_image, corners, ids)

                if id == 1:  
                    self.path_aruco1.append((center_x, center_y))
                    
                    
                    self.prev_aruco1_position = (center_x, center_y)
                    # Calculate the rotation angle
                    rvec,tvec,_ = cv2.aruco.estimatePoseSingleMarkers(corners[i], 1.0, cameraMatrix, distCoeffs)
                    R = cv2.Rodrigues(rvec)[0]
                    angle = np.arctan2(-R[1, 0], -R[0, 0]) 
                    if angle < 0:
                        angle += np.pi

                    # Publish the detected ArUco ID, center, and rotation angle as a Pose2D message
                    pose_msg = Pose2D()
                    pose_msg.x = float(center_x)
                    pose_msg.y = float(center_y)
                    pose_msg.theta = angle
                    self.pose_b1.publish(pose_msg)
                    print(f"ArUco ID: {id}, Center X: {pose_msg.x}, Center Y: {pose_msg.y}, Angle: {pose_msg.theta}")
                
                if id == 2:
                    self.path_aruco2.append((center_x, center_y))
                    
                    
                    self.prev_aruco2_position = (center_x, center_y)
                    rvec,tvec,_ = cv2.aruco.estimatePoseSingleMarkers(corners[i], 1.0, cameraMatrix, distCoeffs)
                    R = cv2.Rodrigues(rvec)[0]
                    angle = np.arctan2(-R[1, 0], -R[0, 0]) 
                    if angle < 0:
                        angle += np.pi
                        
                    pose_msg = Pose2D()
                    pose_msg.x = float(center_x)
                    pose_msg.y = float(center_y)
                    pose_msg.theta = angle
                    self.pose_b2.publish(pose_msg)
                    print(f"ArUco ID: {id}, Center X: {pose_msg.x}, Center Y: {pose_msg.y}, Angle: {pose_msg.theta}")
                    
                elif id ==3:
                    self.path_aruco3.append((center_x, center_y))
                    
                    
                    self.prev_aruco3_position = (center_x, center_y)
                    rvec,tvec,_ = cv2.aruco.estimatePoseSingleMarkers(corners[i], 1.0, cameraMatrix, distCoeffs)
                    R = cv2.Rodrigues(rvec)[0]
                    angle = np.arctan2(-R[1, 0], -R[0, 0]) 
                    if angle < 0:
                        angle += np.pi
                        
                    pose_msg = Pose2D()
                    pose_msg.x = float(center_x)
                    pose_msg.y = float(center_y)
                    pose_msg.theta = angle
                    self.pose_b3.publish(pose_msg)
                    print(f"ArUco ID: {id}, Center X: {pose_msg.x}, Center Y: {pose_msg.y}, Angle: {pose_msg.theta}")
        self.draw_paths()            
        cv2.imshow('ProcessedImage', self.cv_image)
        cv2.waitKey(1)
        
        
    def draw_paths(self):
        self.draw_path(self.path_aruco1, (0, 0, 255))
        self.draw_path(self.path_aruco2, (0, 255, 0))
        self.draw_path(self.path_aruco3, (255, 0, 0))

    def draw_path(self, path, color):
        for i in range(1, len(path)):
            cv2.line(self.cv_image, path[i - 1], path[i], color, 2)


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