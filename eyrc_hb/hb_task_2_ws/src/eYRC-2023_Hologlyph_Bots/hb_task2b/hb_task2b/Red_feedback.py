import cv2
import numpy as np

# Camera intrinsic parameters (replace with your actual camera matrix and distortion coefficients)
cameraMatrix = np.array([[436.89314, 0., 318.41215],
                        [0., 443.85806, 224.55444],
                        [0., 0., 1.]])
distCoeffs = np.array([-0.402946, 0.170450, -0.001775, 0.001639, 0.000000])

# Create an ArUco dictionary and parameters
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
aruco_params = cv2.aruco.DetectorParameters()

# Capture video from the camera (replace 0 with the camera index or video file)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        break

    # Detect ArUco markers in the frame
    corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)

    if ids is not None:
        for i in range(len(ids)):
            # Draw the detected markers on the frame
            cv2.aruco.drawDetectedMarkers(frame, corners)

            # Estimate pose of the detected markers
            rvec, _, _ = cv2.aruco.estimatePoseSingleMarkers(corners[i], 1.0, cameraMatrix, distCoeffs)

            # Convert rotation vector to rotation matrix using Rodrigues
            R, _ = cv2.Rodrigues(rvec)

            # Extract Euler angles from rotation matrix
            yaw = np.arctan2(R[1, 0], R[0, 0])

            # Print the yaw angle
            print("Yaw angle for marker {}:".format(ids[i][0]), yaw)

    # Display the frame
    cv2.imshow('ArUco Detection', frame)

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
