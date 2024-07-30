import camera
import printer

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QStackedLayout, QDialog, QSizePolicy
from PyQt5.QtGui import QPixmap, QScreen, QFont, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTime, QTimer, pyqtSignal, QThreadPool, QRunnable, QObject


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

        # ROW 1
        row1 = QWidget()
        row1_layout = QHBoxLayout()
        title_lable = QLabel('Photobooth')
        title_lable.setAlignment(Qt.AlignCenter)
        row1_layout.addWidget(title_lable)
        row1.setLayout(row1_layout)
        main_layout.addWidget(row1, stretch=1)

        # ROW 2
        row2 = QWidget()
        row2_layout = QHBoxLayout()
        row2_layout.setAlignment(Qt.AlignCenter)

        self.countdown_widget = CountdownWidget()
        self.countdown_widget.countdown_finished.connect(
            self.on_countdown_finished)

        button_col_layout = QVBoxLayout()

        picture_button = QPushButton('Bild machen')
        picture_button.clicked.connect(self.on_picture_button_click)
        button_col_layout.addWidget(picture_button)

        button_col_layout.addWidget(QPushButton('Drucken'))

        mailing_list_button = QPushButton('Mailing List')
        mailing_list_button.clicked.connect(self.mailing_list_dialog)
        button_col_layout.addWidget(mailing_list_button)

        # Image frame
        self.image_widget_layout = QStackedLayout()
        self.image_widget_layout.setAlignment(self.countdown_widget, Qt.AlignCenter)

        self.image_label = QLabel(self)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.white_image_placeholder = QLabel(self)
        self.white_image_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.white_image_placeholder.setText("Loading")
        self.white_image_placeholder.setAlignment(Qt.AlignCenter)
        self.white_image_placeholder.setStyleSheet("background-color: lightblue;")

        self.image_widget_layout.addWidget(self.white_image_placeholder)

        self.countdown_widget_wrapper = QWidget()
        self.countdown_widget_wrapper_layout = QVBoxLayout()
        self.countdown_widget_wrapper_layout.setAlignment(Qt.AlignCenter)
        self.countdown_widget_wrapper.setLayout(self.countdown_widget_wrapper_layout)
        self.countdown_widget_wrapper_layout.addWidget(self.countdown_widget)

        self.image_widget_layout.addWidget(self.countdown_widget_wrapper)
        self.image_widget_layout.addWidget(self.image_label)

        row2.setLayout(row2_layout)
        row2_layout.addLayout(button_col_layout, stretch=1)
        row2_layout.addLayout(self.image_widget_layout, stretch=7)

        main_layout.addWidget(row2, stretch=7)

        self.setLayout(main_layout)

        # Get the screen size
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        self.screen_width = screen.width()
        self.screen_height = screen.height()

        self.resize(1280, 720)
        # TODO uncomment
        # self.resize(self.screen_width, self.screen_height)

        # Apply the stylesheet
        with open('style.css', 'r') as f:
            self.setStyleSheet(f.read())

        self.thread_pool = QThreadPool()

    def on_picture_button_click(self):
        self.image_widget_layout.setCurrentWidget(self.countdown_widget_wrapper)
        self.countdown_widget.start_countdown()

    def on_countdown_finished(self):
        self.image_widget_layout.setCurrentWidget(self.white_image_placeholder)
        self.take_picture_signals = TakePictureSignals()
        picture_task = TakePictureTask(self.take_picture_signals)
        self.take_picture_signals.task_finished.connect(self.display_image)
        self.thread_pool.start(picture_task)

    def display_image(self, image_path):
        if image_path:
            # Load and display the image in the label
            pixmap = QPixmap(image_path)

            pixmap = pixmap.scaled(int(1080 * 0.95), int(587 * 0.95), aspectRatioMode=1)
            self.image_label.setPixmap(pixmap)
            self.image_widget_layout.setCurrentWidget(self.image_label)
            return image_path

    def print(self, image_path):
        printer.print(image_path)

    def mailing_list_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec()


class TakePictureSignals(QObject):
    task_finished = pyqtSignal(str)


class TakePictureTask(QRunnable):

    def __init__(self, signals):
        super(TakePictureTask, self).__init__()
        self.signals = signals

    def run(self):
        file_name = camera.take_picture()
        self.signals.task_finished.emit(file_name)


class CountdownWidget(QWidget):
    countdown_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.total_seconds = 2
        self.update_interval = 1000 // 60  # 60 updates per second

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)

        self.elapsed_time = QTime()
        self.elapsed_time.start()

        self.setFixedSize(300, 300)

    def start_countdown(self):
        self.elapsed_time.restart()
        self.timer.start(self.update_interval)

    def update_countdown(self):
        elapsed_ms = self.elapsed_time.elapsed()
        if elapsed_ms >= self.total_seconds * 1000:
            self.timer.stop()
            self.countdown_finished.emit()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 10

        painter.setPen(QPen(Qt.black, 2))
        # Set the initial circle background to black
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(center, radius, radius)

        elapsed_ms = self.elapsed_time.elapsed()
        if elapsed_ms <= self.total_seconds * 1000:
            angle = int(360 * (elapsed_ms / (self.total_seconds * 1000)))
            painter.setBrush(QColor(90, 0, 0))
            painter.drawPie(rect.adjusted(10, 10, -10, -10),
                            90 * 16, -angle * 16)

        # Draw remaining seconds in the center with a white number and black outline
        remaining_seconds = max(0, self.total_seconds - elapsed_ms // 1000)
        painter.setFont(QFont('Arial', 72, QFont.Bold))
        painter.setPen(QPen(Qt.black, 8))
        painter.drawText(rect, Qt.AlignCenter, str(remaining_seconds))
        painter.setPen(QPen(Qt.white, 3))
        painter.drawText(rect, Qt.AlignCenter, str(remaining_seconds))


if __name__ == '__main__':
    os.environ["XDG_SESSION_TYPE"] = "xcb"

    # Create the application object
    app = QApplication(sys.argv)

    # Create an instance of the ImageApp
    window = PhotoBoothApp()

    # Show the window
    window.show()
    # window.showFullScreen()

    # Run the application's event loop
    sys.exit(app.exec_())
