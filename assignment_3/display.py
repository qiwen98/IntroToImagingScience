import numpy as np
import time
import platform
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2

class FringePatternWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up the main window
        self.setWindowTitle("Fringe Patterns")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Get screen size
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        print(f"Detected screen resolution: {self.screen_width} x {self.screen_height} pixels")
        
        # Adjust for Retina display scaling if needed
        self.is_macos = platform.system() == 'Darwin'
        if self.is_macos:
            # The scaling factor is usually 2 for Retina displays
            # PyQt5 handles this automatically, so we don't need to multiply
            pass
            
        # Set up the label to display images
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)
        
        # Initialize variables
        self.current_image_index = 0
        self.all_images = []
        self.interval_seconds = 2.0  # Default value
        
        # Timer for image transitions
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_image)
    
    def generate_sinusoidal_fringe_pattern(self, shape, amplitude=1.0, background=1.0, orientation='vertical'):
        """
        Generate an initial image with a sinusoidal fringe pattern of one period.
        Parameters:
        - shape: Tuple (height, width) of the image.
        - amplitude: Amplitude of the sinusoidal pattern.
        - background: Background intensity (DC component).
        - orientation: 'vertical' for vertical fringes, 'horizontal' for horizontal fringes.
        Returns:
        - initial_image: Initial image with sinusoidal fringe pattern.
        - true_phase: True phase map of the fringe pattern.
        """
        height, width = shape
        if orientation == 'vertical':
            x = np.linspace(0, 2 * np.pi, width) # One period across the width
            X = np.tile(x, (height, 1)) # Repeat the pattern vertically
            true_phase = X # Phase varies from 0 to 2pi across the width
        elif orientation == 'horizontal':
            phase_shift = np.pi/2
            scaled_height = height/width * 2 * np.pi
            initial_y_offset = (2 * np.pi - scaled_height)/2
            y = np.linspace(initial_y_offset - phase_shift, (scaled_height + initial_y_offset - phase_shift), height)
            Y = np.tile(y, (width, 1)).T # Repeat the pattern horizontally
            true_phase = Y # Phase varies from 0 to 2pi across the height
        else:
            raise ValueError("Orientation must be 'vertical' or 'horizontal'")
        initial_image = background + amplitude * np.cos(true_phase)
        return initial_image, true_phase
    
    def generate_phase_shifted_images(self, shape, orientation):
        phase_shifts = [0, np.pi/2, np.pi, 3*np.pi/2]
        images = []
        
        for phase_shift in phase_shifts:
            # Generate base pattern
            image, true_phase = self.generate_sinusoidal_fringe_pattern(
                shape, amplitude=1.0, background=1.0, orientation=orientation
            )
            
            # Apply phase shift
            if orientation == 'vertical':
                shifted_phase = true_phase + phase_shift
            else:
                # For horizontal, phase shift is already handled in the generation function
                # We'll apply additional shift
                shifted_phase = true_phase + phase_shift
                
            # Generate image with shifted phase
            shifted_image = 1.0 + 1.0 * np.cos(shifted_phase)
            
            # Scale to 8-bit for display (0-255)
            shifted_image_8bit = (shifted_image * 127.5).astype(np.uint8)
            
            images.append(shifted_image_8bit)
        
        return images
    
    def prepare_images(self):
        # Generate all fringe patterns
        vertical_images = self.generate_phase_shifted_images((self.screen_height, self.screen_width), orientation='vertical')
        horizontal_images = self.generate_phase_shifted_images((self.screen_height, self.screen_width), orientation='horizontal')
        self.all_images = vertical_images + horizontal_images
        print(f"Generated {len(self.all_images)} fringe pattern images")
    
    def start_display(self, interval_seconds):
        self.interval_seconds = interval_seconds
        self.showFullScreen()
        self.current_image_index = 0
        self.show_image(self.current_image_index)
        self.timer.start(int(self.interval_seconds * 1000))  # Convert to milliseconds
    
    def show_image(self, index):
        if 0 <= index < len(self.all_images):
            print(f"Displaying image {index+1} of {len(self.all_images)}")
            image = self.all_images[index]
            
            # Convert OpenCV image to QImage
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            
            # Display the image
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.screen_width, self.screen_height, 
                                                    Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
    
    def show_next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.all_images):
            self.timer.stop()
            self.close()
            return
        
        self.show_image(self.current_image_index)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q or event.key() == Qt.Key_Escape:
            self.timer.stop()
            self.close()

def main():
    app = QApplication(sys.argv)
    window = FringePatternWindow()
    
    # Generate the fringe patterns
    window.prepare_images()
    
    # Get user-defined interval
    try:
        interval_seconds = float(input("Enter the display interval in seconds (e.g., 2.0): "))
    except ValueError:
        interval_seconds = 2.0
        print("Invalid input, using default value of 2.0 seconds")
    
    # Start displaying images
    window.start_display(interval_seconds)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()