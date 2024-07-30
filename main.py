import camera
import printer

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QScreen


class ImageApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the UI
        self.initUI()

    def initUI(self):
        # Set window title
        self.setWindowTitle('Load Image on Button Click')

        # Set up the layout
        self.layout = QVBoxLayout()

        # Create a button and connect it to the load_image method
        self.button = QPushButton('Load Image', self)
        self.button.clicked.connect(self.load_image)
        self.layout.addWidget(self.button)

        # Create a label to display the image
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        # Set the layout for the main window
        self.setLayout(self.layout)

        # Set window size
        self.resize(400, 300)

    def load_image(self):
        # Open a file dialog to select an image file
        file_name = camera.take_picture()
        if file_name:
            # Load and display the image in the label
            pixmap = QPixmap(file_name)

            # Get the screen size
            screen = QScreen.availableGeometry(QApplication.primaryScreen())
            screen_width = screen.width()
            screen_height = screen.height()

            # Calculate the target size (80% of the larger dimension)
            scale_factor = 0.8
            target_size = int(min(screen_width, screen_height) * scale_factor)

            # Scale the pixmap to fit 80% of the screen's larger dimension
            pixmap = pixmap.scaled(target_size, target_size, aspectRatioMode=1)

            self.image_label.setPixmap(pixmap)
            # Scale the image to fit the label size
            self.image_label.setScaledContents(True)
            self.image_label.adjustSize()  # Adjust the size of the label to fit the image


if __name__ == '__main__':
    os.environ["XDG_SESSION_TYPE"] = "xcb"

    # Create the application object
    app = QApplication(sys.argv)

    # Create an instance of the ImageApp
    window = ImageApp()

    # Show the window
    window.show()

    # Run the application's event loop
    sys.exit(app.exec_())
