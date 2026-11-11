# foot_detector.py
import cv2
import mediapipe as mp
import numpy as np

class FootDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_foot_landmarks(self, image):
        """Detect foot landmarks using MediaPipe Pose"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        foot_landmarks = []
        if results.pose_landmarks:
            # Foot landmarks indices in MediaPipe Pose
            # Left foot: 27, 28, 29, 30, 31, 32
            # Right foot: 27, 28, 29, 30, 31, 32 (add 11 to left foot indices for right foot)
            left_foot_indices = [27, 28, 29, 30, 31, 32]
            right_foot_indices = [l + 11 for l in left_foot_indices]
            
            h, w, _ = image.shape
            
            for idx in left_foot_indices + right_foot_indices:
                if idx < len(results.pose_landmarks.landmark):
                    landmark = results.pose_landmarks.landmark[idx]
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    foot_landmarks.append((x, y))
        
        return foot_landmarks, results.pose_landmarks
    
    def draw_foot_landmarks(self, image, landmarks):
        """Draw detected foot landmarks on image"""
        for (x, y) in landmarks:
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        return image
    
    def get_foot_boundary(self, landmarks):
        """Calculate foot boundary points"""
        if not landmarks:
            return None
        
        xs = [p[0] for p in landmarks]
        ys = [p[1] for p in landmarks]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        return (min_x, min_y, max_x, max_y)