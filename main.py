# main.py - UPDATED WITH ERROR HANDLING
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
from kivy.lang import Builder
import cv2
import numpy as np

from foot_detector import FootDetector
from measurement_logic import MeasurementSystem
from size_matcher import SizeMatcher

# Load KV files
Builder.load_file('ui/camera_screen.kv')
Builder.load_file('ui/results_screen.kv')

class CameraWidget(Camera):
    """Custom camera widget for OpenCV processing"""
    pass

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize components
        self.foot_detector = FootDetector()
        self.measurement_system = MeasurementSystem()
        self.size_matcher = SizeMatcher()
        
        # Process frames
        Clock.schedule_interval(self.process_frame, 1.0/30.0)
        
        # Store the captured image for results screen
        self.captured_image = None
        self.measurement_results = None
    
    def on_enter(self):
        """Called when screen becomes active"""
        # Ensure camera is playing
        camera_widget = self.ids.camera_widget
        if not camera_widget.play:
            camera_widget.play = True
    
    def process_frame(self, dt):
        """Process each camera frame for real-time detection"""
        camera_widget = self.ids.camera_widget
        if camera_widget and camera_widget.texture:
            try:
                # Convert texture to OpenCV image
                texture = camera_widget.texture
                image = self.texture_to_cv2(texture)
                
                # Preprocess image
                processed_image = self.measurement_system.preprocess_image(image)
                
                # Detect reference object (can return None)
                reference_points = self.measurement_system.detect_reference_object(processed_image)
                
                if reference_points is not None:
                    # Draw reference object - handle both chessboard and A4 paper
                    if isinstance(reference_points, np.ndarray) and len(reference_points) > 0:  # Chessboard corners
                        # Only draw if we have valid corners
                        if reference_points.shape[0] == self.measurement_system.pattern_size[0] * self.measurement_system.pattern_size[1]:
                            cv2.drawChessboardCorners(processed_image, self.measurement_system.pattern_size, reference_points, True)
                            self.ids.instruction_label.text = "Chessboard detected - Ready for calibration"
                        else:
                            self.ids.instruction_label.text = "Place calibration pattern or A4 paper in frame"
                    else:  # A4 paper contour
                        cv2.drawContours(processed_image, [reference_points], -1, (0, 255, 0), 2)
                        self.ids.instruction_label.text = "A4 paper detected - Ready for calibration"
                else:
                    self.ids.instruction_label.text = "Place calibration pattern or A4 paper in frame"
                
                # Detect foot landmarks
                foot_landmarks, pose_landmarks = self.foot_detector.detect_foot_landmarks(processed_image)
                
                if foot_landmarks:
                    # Draw foot landmarks
                    processed_image = self.foot_detector.draw_foot_landmarks(processed_image, foot_landmarks)
                    
                    # Get foot boundary
                    foot_boundary = self.foot_detector.get_foot_boundary(foot_landmarks)
                    
                    if foot_boundary:
                        # Draw foot boundary
                        min_x, min_y, max_x, max_y = foot_boundary
                        cv2.rectangle(processed_image, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)
                        self.ids.instruction_label.text = "Foot detected - Ready to measure"
                
                # Convert back to texture and display
                self.display_cv2_image(processed_image)
                
            except Exception as e:
                print(f"Error in process_frame: {e}")
                # Continue running even if there's an error in one frame
    
    def texture_to_cv2(self, texture):
        """Convert Kivy texture to OpenCV image"""
        size = texture.size
        pixels = texture.pixels
        image = np.frombuffer(pixels, np.uint8)
        image = image.reshape(size[1], size[0], 4)
        return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    
    def display_cv2_image(self, image):
        """Display OpenCV image in Kivy"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Flip vertically (camera mirroring)
        buf = image_rgb.tobytes()
        
        # Create texture
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        
        # Update camera texture
        self.ids.camera_widget.texture = texture
    
    def calibrate_reference(self):
        """Enhanced calibration using chessboard pattern"""
        camera_widget = self.ids.camera_widget
        if camera_widget.texture:
            image = self.texture_to_cv2(camera_widget.texture)
            
            # Try chessboard calibration first (more accurate)
            if self.measurement_system.calibrate_with_chessboard(image):
                self.ids.instruction_label.text = "Chessboard calibration successful! High accuracy achieved."
                return
            
            # Fallback to A4 paper detection
            reference_points = self.measurement_system.detect_a4_paper(image)
            
            if reference_points is not None and len(reference_points) >= 4:
                calib_points = [reference_points[0], reference_points[2]]
                success = self.measurement_system.calibrate_with_reference(image, calib_points)
                
                if success:
                    self.ids.instruction_label.text = "A4 paper calibration successful!"
                else:
                    self.show_error("A4 paper calibration failed")
            else:
                self.show_error("Place calibration pattern or A4 paper in frame")
    
    def measure_foot(self):
        """Capture image and perform measurement"""
        camera_widget = self.ids.camera_widget
        if camera_widget.texture:
            # Capture current frame
            self.captured_image = self.texture_to_cv2(camera_widget.texture)
            processed_image = self.measurement_system.preprocess_image(self.captured_image)
            
            # Detect foot landmarks
            foot_landmarks, _ = self.foot_detector.detect_foot_landmarks(processed_image)
            
            if foot_landmarks:
                foot_boundary = self.foot_detector.get_foot_boundary(foot_landmarks)
                
                if foot_boundary:
                    if self.measurement_system.calibration_factor:
                        foot_length_cm = self.measurement_system.measure_foot_length(foot_boundary)
                        
                        if foot_length_cm:
                            recommended_size = self.size_matcher.recommend_size(foot_length_cm)
                            
                            # Store results for results screen
                            self.measurement_results = {
                                'foot_length': foot_length_cm,
                                'size': recommended_size,
                                'image': self.captured_image
                            }
                            
                            # Switch to results screen
                            self.manager.current = 'results'
                            self.manager.get_screen('results').display_results(self.measurement_results)
                        else:
                            self.show_error("Measurement calculation failed")
                    else:
                        self.show_error("Please calibrate first")
                else:
                    self.show_error("Could not determine foot boundary")
            else:
                self.show_error("Foot not detected - ensure foot is visible")
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class ResultsScreen(Screen):
    def display_results(self, results):
        """Display measurement results"""
        foot_length = results['foot_length']
        size = results['size']
        image = results['image']
        
        # Update labels
        self.ids.result_label.text = f'Foot Length: {foot_length:.2f} cm'
        self.ids.size_label.text = f'Recommended Size: {size}'
        
        # Convert and display the captured image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_flipped = cv2.flip(image_rgb, 0)  # Flip vertically
        
        # Save temporary image for display
        cv2.imwrite('temp_result.jpg', image_flipped)
        self.ids.result_image.source = 'temp_result.jpg'
    
    def measure_again(self):
        """Go back to camera screen for new measurement"""
        self.manager.current = 'camera'
    
    def save_results(self):
        """Save measurement results (placeholder)"""
        # You can implement saving to file or database here
        self.show_popup("Results Saved", "Measurement results have been saved successfully!")
    
    def show_popup(self, title, message):
        """Show information popup"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class FootMeasurementApp(App):
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        sm.add_widget(CameraScreen(name='camera'))
        sm.add_widget(ResultsScreen(name='results'))
        return sm

if __name__ == '__main__':
    FootMeasurementApp().run()