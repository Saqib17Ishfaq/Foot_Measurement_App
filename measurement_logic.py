# measurement_logic.py - COMPLETE WITH CHESSBOARD CALIBRATION
import cv2
import numpy as np
import os

class MeasurementSystem:
    def __init__(self):
        self.reference_length_cm = 21.0  # A4 paper width
        self.calibration_factor = None
        self.pattern_size = (9, 6)  # Chessboard pattern size (9x6)
    
    def preprocess_image(self, image):
        """Enhance image for better detection"""
        # Adjust contrast and brightness
        alpha = 1.2  # Contrast control
        beta = 10   # Brightness control
        enhanced = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        
        # Reduce noise
        denoised = cv2.medianBlur(enhanced, 5)
        
        return denoised
    
    def calibrate_with_reference(self, image, reference_points):
        """Calibrate using a reference object (A4 paper, credit card)"""
        if len(reference_points) >= 2:
            # Calculate pixel distance between reference points
            ref_distance_pixels = np.linalg.norm(
                np.array(reference_points[0]) - np.array(reference_points[1])
            )
            
            # Calculate pixels per cm
            self.calibration_factor = ref_distance_pixels / self.reference_length_cm
            return True
        return False
    
    def measure_foot_length(self, foot_boundary):
        """Measure foot length in centimeters"""
        if not foot_boundary or self.calibration_factor is None:
            return None
        
        min_x, min_y, max_x, max_y = foot_boundary
        foot_length_pixels = max_y - min_y
        foot_length_cm = foot_length_pixels / self.calibration_factor
        
        return foot_length_cm
    
    def calibrate_with_chessboard(self, image):
        """Calibrate using chessboard pattern for high accuracy"""
        corners = self.detect_chessboard_corners(image)
        
        if corners is not None and len(corners) >= 2:
            # Calculate distance between first and last corner (diagonal of pattern)
            point1 = corners[0][0]  # Top-left corner
            point2 = corners[-1][0] # Bottom-right corner
            
            # Known real-world size: pattern is 175mm x 125mm (standard OpenCV pattern)
            real_world_diagonal_mm = np.sqrt(175**2 + 125**2)  # ~214.6mm
            real_world_diagonal_cm = real_world_diagonal_mm / 10  # ~21.46cm
            
            # Pixel distance
            pixel_distance = np.linalg.norm(point1 - point2)
            
            # Calculate calibration factor (pixels per cm)
            self.calibration_factor = pixel_distance / real_world_diagonal_cm
            return True
        
        return False
    
    def detect_chessboard_corners(self, image):
        """Detect chessboard corners for precise calibration"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, self.pattern_size, None)
        
        if ret:
            # Refine corner detection
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            return corners
        return None
    
    def detect_reference_object(self, image):
        """Enhanced detection using chessboard pattern OR A4 paper"""
        # First try chessboard pattern
        corners = self.detect_chessboard_corners(image)
        if corners is not None:
            return corners
        
        # Fallback to A4 paper detection
        return self.detect_a4_paper(image)
    
    def detect_a4_paper(self, image):
        """A4 paper detection code"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 4:
                rect = cv2.minAreaRect(contour)
                width, height = rect[1]
                aspect_ratio = max(width, height) / min(width, height)
                
                if 1.3 < aspect_ratio < 1.5:
                    return approx.reshape(4, 2)
        
        return None