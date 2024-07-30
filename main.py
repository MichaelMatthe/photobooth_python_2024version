import camera
import printer

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QDialog
from PyQt5.QtGui import QPixmap, QScreen
from PyQt5.QtCore import Qt


class PhotoBoothApp(QWidget):

    def __init__(self):
        super().__init__()

        # Initialize the UI
        self.initUI()

    def initUI(self):
        # Set window title
        self.setWindowTitle('Photobooth')

        # Set up the layout
        main_layout = QVBoxLayout()

        row1 = QWidget()
        row1_layout = QHBoxLayout()
        title_lable = QLabel('Photobooth')
        title_lable.setAlignment(Qt.AlignCenter)
        row1_layout.addWidget(title_lable)
        row1.setLayout(row1_layout)
        main_layout.addWidget(row1, stretch=1)

        row2 = QWidget()
        row2_layout = QHBoxLayout()

        button_col = QWidget()
        button_col_layout = QVBoxLayout()
        picture_button = QPushButton('Bild machen')
        picture_button.clicked.connect(self.take_picture)
        button_col_layout.addWidget(picture_button)
        button_col_layout.addWidget(QPushButton('Drucken'))
        mailing_list_button = QPushButton('Mailing List')
        mailing_list_button.clicked.connect(self.mailing_list_dialog)
        button_col_layout.addWidget(mailing_list_button)
        button_col.setLayout(button_col_layout)
        row2_layout.addWidget(button_col, stretch=1)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        row2_layout.addWidget(self.image_label, stretch=7)
        row2.setLayout(row2_layout)
        main_layout.addWidget(row2, stretch=7)

        self.setLayout(main_layout)

        # Get the screen size
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        self.resize(1280, 720)
        # TODO uncomment
        #self.resize(self.screen_width, self.screen_height)

        # Apply the stylesheet
        with open('style.css', 'r') as f:
            self.setStyleSheet(f.read())

    def take_picture(self):
        file_name = camera.take_picture()
        if file_name:
            # Load and display the image in the label
            pixmap = QPixmap(file_name)

            # Calculate the target size (80% of the larger dimension)
            scale_factor = 0.95
            # Scale the pixmap to fit 80% of the screen's larger dimension
            pixmap = pixmap.scaled(int(self.image_label.width() * scale_factor), int(self.image_label.height() * scale_factor), aspectRatioMode=1)
            self.image_label.setPixmap(pixmap)

    def mailing_list_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec()


if __name__ == '__main__':
    os.environ["XDG_SESSION_TYPE"] = "xcb"

    # Create the application object
    app = QApplication(sys.argv)

    # Create an instance of the ImageApp
    window = PhotoBoothApp()

    # Show the window
    window.show()
    #window.showFullScreen()

    # Run the application's event loop
    sys.exit(app.exec_())
