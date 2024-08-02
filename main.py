import camera
import printer
import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QHBoxLayout, QStackedLayout, QDialog, QSizePolicy)
from PyQt5.QtGui import QPixmap, QScreen, QFont, QPainter, QPen, QColor, QFontDatabase
from PyQt5.QtCore import Qt, QTime, QTimer, pyqtSignal, QThreadPool, QRunnable, QObject, QSize, QRect


class PhotoBoothApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.thread_pool = QThreadPool()

    def initUI(self):
        self.setWindowTitle('Photobooth')

        self.main_layout_overlay = QStackedLayout()

        self.white_widget = QWidget()
        self.white_widget.setStyleSheet('background-color: white;')
        self.main_widget = QWidget()
        self.main_layout_overlay.addWidget(self.main_widget)
        self.main_layout_overlay.addWidget(self.white_widget)
        main_layout = QVBoxLayout()
        self.main_widget.setLayout(main_layout)

        main_layout.addWidget(self.create_title_label(), stretch=1)
        main_layout.addLayout(self.create_main_layout(), stretch=7)

        self.setLayout(self.main_layout_overlay)
        self.resize_app()
        self.apply_stylesheet()

    def create_title_label(self):
        title_label = QLabel('Photobooth')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 24))
        return title_label

    def create_main_layout(self):
        row_layout = QHBoxLayout()
        row_layout.setAlignment(Qt.AlignCenter)

        button_col_layout = self.create_button_column()
        self.image_widget_layout = self.create_image_layout()

        row_layout.addLayout(button_col_layout, stretch=1)
        row_layout.addLayout(self.image_widget_layout, stretch=7)

        return row_layout

    def create_button_column(self):
        button_col_layout = QVBoxLayout()
        picture_button = QPushButton('Bild machen')
        picture_button.clicked.connect(self.on_picture_button_click)
        button_col_layout.addWidget(picture_button)

        print_button = QPushButton('Drucken')
        print_button.clicked.connect(self.print_current_image)
        button_col_layout.addWidget(print_button)

        mailing_list_button = QPushButton('Mailing List')
        mailing_list_button.clicked.connect(self.mailing_list_dialog)
        button_col_layout.addWidget(mailing_list_button)

        return button_col_layout

    def create_image_layout(self):
        image_layout = QStackedLayout()
        initial_label = QLabel(self)

        self.countdown_widget = CountdownWidget()
        self.countdown_widget.countdown_finished.connect(
            self.on_countdown_finished)

        self.image_label = QLabel(self)
        self.image_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.white_image_placeholder = QLabel("Loading...", self)
        self.white_image_placeholder.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.white_image_placeholder.setAlignment(Qt.AlignCenter)

        self.countdown_widget_wrapper = QWidget()
        countdown_widget_wrapper_layout = QVBoxLayout()
        countdown_widget_wrapper_layout.setAlignment(Qt.AlignCenter)
        self.countdown_widget_wrapper.setLayout(
            countdown_widget_wrapper_layout)
        countdown_widget_wrapper_layout.addWidget(self.countdown_widget)

        image_layout.addWidget(initial_label)
        image_layout.addWidget(self.white_image_placeholder)
        image_layout.addWidget(self.countdown_widget_wrapper)
        image_layout.addWidget(self.image_label)

        return image_layout

    def resize_app(self):
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        self.resize(1280, 720)

    def apply_stylesheet(self):
        try:
            with open('style.css', 'r') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet file 'style.css' not found.")

    def on_picture_button_click(self):
        self.image_widget_layout.setCurrentWidget(
            self.countdown_widget_wrapper)
        self.countdown_widget.start_countdown()

    def on_countdown_finished(self):
        self.main_layout_overlay.setCurrentWidget(self.white_widget)
        self.image_widget_layout.setCurrentWidget(self.white_image_placeholder)
        self.take_picture_signals = TakePictureSignals()
        picture_task = TakePictureTask(self.take_picture_signals)
        self.take_picture_signals.task_finished.connect(self.display_image)
        self.thread_pool.start(picture_task)

    def display_image(self, image_path):
        if image_path:
            pixmap = QPixmap(image_path).scaled(
                int(1080 * 0.95), int(587 * 0.95), Qt.KeepAspectRatio)

            border_width = 10
            # Create a new pixmap with the border
            size = pixmap.size() + QSize(2 * border_width, 2 * border_width)
            bordered_pixmap = QPixmap(size)
            # Fill with white color
            bordered_pixmap.fill(QColor(255, 255, 255))

            painter = QPainter(bordered_pixmap)

            # Draw the original pixmap onto the new one
            painter.drawPixmap(border_width, border_width, pixmap)

            # Draw the border
            border_rect = QRect(0, 0, size.width(), size.height())
            painter.setPen(QColor(255, 255, 255))  # White border color
            painter.drawRect(border_rect)  # Draw border around the pixmap

            painter.end()

            self.image_label.setPixmap(bordered_pixmap)
            self.image_widget_layout.setCurrentWidget(self.image_label)
            self.main_layout_overlay.setCurrentWidget(self.main_widget)

    def print_current_image(self):
        image_path = self.image_label.pixmap().cacheKey()
        if image_path:
            printer.print(image_path)

    def mailing_list_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Mailing List")
        dlg.exec()


class TakePictureSignals(QObject):
    task_finished = pyqtSignal(str)


class TakePictureTask(QRunnable):
    def __init__(self, signals):
        super(TakePictureTask, self).__init__()
        self.signals = signals

    def run(self):
        try:
            file_name = camera.take_picture()
            self.signals.task_finished.emit(file_name)
        except Exception as e:
            print(f"Error taking picture: {e}")
            self.signals.task_finished.emit("")


class CountdownWidget(QWidget):
    countdown_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.total_seconds = 4
        self.update_interval = 1000 // 60  # 60 updates per second

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)

        self.elapsed_time = QTime()
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
        # painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(center, radius, radius)

        elapsed_ms = self.elapsed_time.elapsed()
        if elapsed_ms <= self.total_seconds * 1000:
            angle = int(360 * (elapsed_ms / (self.total_seconds * 1000)))
            painter.setBrush(QColor(255, 255, 224))
            painter.setPen(Qt.NoPen)
            painter.drawPie(rect.adjusted(10, 10, -10, -10),
                            90 * 16, -angle * 16)

        remaining_seconds = max(0, self.total_seconds - elapsed_ms // 1000)
        painter.setFont(QFont('Bungee', 144, QFont.Bold))
        painter.setPen(QPen(Qt.black, 8))
        painter.drawText(rect, Qt.AlignCenter, str(remaining_seconds))


if __name__ == '__main__':
    os.environ["XDG_SESSION_TYPE"] = "xcb"

    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont("fonts/Bungee-Regular.ttf")
    window = PhotoBoothApp()
    window.show()
    sys.exit(app.exec_())
