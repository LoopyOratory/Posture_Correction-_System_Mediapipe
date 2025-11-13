import json
import cv2
import mediapipe as mp
import numpy as np
import base64
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class PostureConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize webcam capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Start processing
        self.is_running = True
        asyncio.create_task(self.process_video())

    async def disconnect(self, close_code):
        self.is_running = False
        if hasattr(self, 'cap'):
            self.cap.release()
        if hasattr(self, 'pose'):
            self.pose.close()

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        data = json.loads(text_data)
        command = data.get('command')
        
        if command == 'stop':
            self.is_running = False
        elif command == 'start':
            self.is_running = True
            asyncio.create_task(self.process_video())

    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        angle_degrees = np.degrees(angle)
        
        if angle_degrees > 180.0:
            angle_degrees = 360 - angle_degrees
            
        return angle_degrees

    async def process_video(self):
        """Process video frames and send to frontend"""
        while self.is_running:
            success, image = self.cap.read()
            
            if not success:
                await asyncio.sleep(0.01)
                continue

            image_height, image_width, _ = image.shape
            
            # Process image
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            
            image.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            
            posture_data = {
                'posture': 'Unknown',
                'angle': 0,
                'color': [255, 255, 255]
            }
            
            # Extract landmarks
            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    
                    # Get coordinates
                    shoulder = [
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                    ]
                    hip = [
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y
                    ]
                    knee = [
                        landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y
                    ]
                    
                    # Calculate angle
                    angle = self.calculate_angle(shoulder, hip, knee)
                    hip_pixel = tuple(np.multiply(hip, [image_width, image_height]).astype(int))
                    
                    # Determine posture
                    if angle > 90:
                        posture = "Good Posture"
                        color = (0, 255, 0)
                    else:
                        posture = "Bad Posture"
                        color = (0, 0, 255)
                    
                    posture_data = {
                        'posture': posture,
                        'angle': int(angle),
                        'color': color
                    }
                    
                    # Draw on image
                    cv2.putText(image, f"Angle: {int(angle)}", 
                              (hip_pixel[0] - 50, hip_pixel[1] - 50),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    cv2.rectangle(image, (10, 10), (450, 70), (40, 40, 40), -1)
                    cv2.putText(image, "POSTURE:", (20, 35),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, posture, (140, 40),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
                    
                    # Draw landmarks
                    self.mp_drawing.draw_landmarks(
                        image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                        self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                    )
            except Exception as e:
                pass
            
            # Encode image to base64
            _, buffer = cv2.imencode('.jpg', image)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')
            
            # Send frame to frontend
            await self.send(text_data=json.dumps({
                'frame': jpg_as_text,
                'posture': posture_data['posture'],
                'angle': posture_data['angle']
            }))
            
            # Control frame rate (~30 FPS)
            await asyncio.sleep(0.033)