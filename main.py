import camera
import printer
import sys
import re
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QHBoxLayout, QStackedLayout, QDialog, QSizePolicy, 
                             QLineEdit, QMessageBox)
from PyQt5.QtGui import QPixmap, QScreen, QFont, QPainter, QPen, QColor, QFontDatabase
from PyQt5.QtCore import (Qt, QTime, QTimer, pyqtSignal, QThreadPool, QRunnable, 
                          QObject, QSize, QRect)


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
        title_label.setObjectName('titleLable')
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
        self.button_col_layout = QVBoxLayout()
        self.picture_button = QPushButton('Bild machen')
        self.picture_button.clicked.connect(self.on_picture_button_click)
        self.button_col_layout.addWidget(self.picture_button)

        self.print_button = QPushButton('Drucken')
        self.print_button.clicked.connect(self.print_current_image)
        self.button_col_layout.addWidget(self.print_button)
        self.print_button.setEnabled(False)

        self.mailing_list_button = QPushButton('Mailing List')
        self.mailing_list_button.clicked.connect(self.show_email_dialog)
        self.button_col_layout.addWidget(self.mailing_list_button)

        return self.button_col_layout

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
        self.picture_button.setEnabled(False)
        self.print_button.setEnabled(False)
        self.mailing_list_button.setEnabled(False)
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
        self.picture_button.setEnabled(True)
        self.mailing_list_button.setEnabled(True)
        if image_path:
            self.print_button.setEnabled(True)
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
        else:

            pixmap = QPixmap(1080, 587)
            pixmap.fill(Qt.white)  # Fill the pixmap with a white background

            # Draw text on the QPixmap
            painter = QPainter(pixmap)
            painter.setPen(QColor(Qt.black))
            font = QFont('Bungee', 40)
            painter.setFont(font)
            
            # Calculate the text position
            text = "Kamerafehler"
            text_rect = painter.boundingRect(pixmap.rect(), Qt.AlignCenter, text)
            
            # Draw the text in the center
            painter.drawText(text_rect, Qt.AlignCenter, text)
            painter.end()

            self.image_label.setPixmap(pixmap)
            self.image_widget_layout.setCurrentWidget(self.image_label)
            self.main_layout_overlay.setCurrentWidget(self.main_widget)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Kamerafehler")
            msg.setText("- Leerer Kamerakku?\n- Leerer Blitzakku?\n- Kamera nicht verbunden?")
    
            # Display the message box
            msg.exec_()
            

    def print_current_image(self):
        image_path = self.image_label.pixmap().cacheKey()
        if image_path:
            printer.print(image_path)

    def show_email_dialog(self):
        dialog = EmailDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            email = dialog.get_email_address()
            if email:
                QMessageBox.information(self, 'E-Mail Adresse', f'E-Mail Adresse hinzugefügt: {email}')
                try:
                    # Open the file in append mode. Create the file if it doesn't exist.
                    with open('email_adressen.txt', 'a') as file:
                        # Write the email address followed by a newline
                        file.write(email + '\n')
                except Exception as e:
                    print(f"An error occurred: {e}")


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
        self.total_seconds = 2
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


class EmailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('E-Mail Adresse für Fotoalbum')
        self.setGeometry(100, 100, 300, 150)
        
        self.email_address = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.label = QLabel('E-Mail Adresse angeben, um Link \nzum Fotoalbum zu erhalten:', self)
        layout.addWidget(self.label)
        
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('E-Mail Adresse')
        layout.addWidget(self.email_input)
        
        self.submit_button = QPushButton('Hinzufügen', self)
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
        
    def on_submit(self):
        email = self.email_input.text()
        
        if self.is_valid_email(email):
            self.email_address = email
            self.accept()  # Close dialog with accept status
        else:
            QMessageBox.warning(self, 'Ungültige E-Mail-Adresse', 'Bitte gültige E-Mail Adresse angeben.')

    def is_valid_email(self, email):
        # Simple regex for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def get_email_address(self):
        return self.email_address

if __name__ == '__main__':
    os.environ["XDG_SESSION_TYPE"] = "xcb"

    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont("fonts/Bungee-Regular.ttf")
    window = PhotoBoothApp()
    window.show()
    sys.exit(app.exec_())
