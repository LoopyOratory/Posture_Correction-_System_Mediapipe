import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b , c):
    """
    Calculates the angle between three points (in 2D).
    Args:
        a, b, c: Each is a tuple or list representing the (x, y) coordinates of a landmark.
                 'b' is the vertex of the angle.
    Returns:
        The calculated angle in degrees.
    """
    # Convert points to numpy arrays
    a = np.array(a)  # First point (e.g., shoulder)
    b = np.array(b)  # Midpoint (e.g., hip)
    c = np.array(c)  # End point (e.g., knee)

    # Calculate vectors
    ba = a - b
    bc = c - b

    # Calculate the angle using the dot product formula
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    # Convert angle to degrees
    angle_degrees = np.degrees(angle)

    # Ensure the angle is within a reasonable range
    if angle_degrees > 180.0:
        angle_degrees = 360 - angle_degrees
        
    return angle_degrees

def main():
    """
    Main function to run the posture detection application.
    """
    # Start capturing video from the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    posture = ""

    while cap.isOpened():
        # Read a frame from the webcam
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Get the dimensions of the frame
        image_height, image_width, _ = image.shape

        # To improve performance, optionally mark the image as not writeable to pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and find pose landmarks
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks if available
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for shoulder, hip, and knee (we'll use the left side)
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            # Calculate the angle at the hip
            angle = calculate_angle(shoulder, hip, knee)

            # Convert hip coordinates to pixel values for displaying text
            hip_pixel_coords = tuple(np.multiply(hip, [image_width, image_height]).astype(int))
            
            # --- Posture Logic ---
            # You can adjust these thresholds based on your preference
            if angle > 90:
                posture = "Good Posture"
                color = (0, 255, 0) # Green
            else:
                posture = "Bad Posture"
                color = (0, 0, 255) # Red

            # --- Visualization ---
            # Display the calculated angle
            cv2.putText(image, f"Angle: {int(angle)}", 
                        (hip_pixel_coords[0] - 50, hip_pixel_coords[1] - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # Display the posture status in a box
            cv2.rectangle(image, (10, 10), (250, 70), (40, 40, 40), -1)
            cv2.putText(image, "POSTURE:", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, posture, (140, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            
            # Draw the landmarks and connections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                       mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                       mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                       )
        except Exception as e:
            # If no landmarks are detected, do nothing
            # You can uncomment the line below to see errors
            # print(f"Error: {e}") 
            pass

        # Display the resulting frame
        cv2.imshow('Sitting Posture Detector', image)

        # Exit the loop when 'q' is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    pose.close()

if __name__ == '__main__':
    main()
