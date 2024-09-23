import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar, QColorDialog, QListWidget, QDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from video_generator import generate_video

class VideoGeneratorThread(QThread):
    progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        generate_video(
            self.params['audio_path'],
            self.params['image_path'],
            self.params['heading_text'],
            self.params['font'],
            self.params['heading_color'],
            self.params['outline_color'],
            self.params['wave_color'],
            self.params['output_path'],
            progress_callback=self.progress_update.emit,
            log_callback=self.log_update.emit
        )

class CustomFileBrowser(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = os.path.expanduser('~')
        self.selected_file = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.path_display = QLineEdit(self.current_path)
        self.path_display.setReadOnly(True)
        layout.addWidget(self.path_display)

        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.item_double_clicked)
        layout.addWidget(self.file_list)

        button_layout = QHBoxLayout()
        self.up_button = QPushButton('Up')
        self.up_button.clicked.connect(self.go_up)
        self.select_button = QPushButton('Select')
        self.select_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.select_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('Custom File Browser')
        self.resize(400, 300)

        self.update_file_list()

    def update_file_list(self):
        self.file_list.clear()
        try:
            for item in os.listdir(self.current_path):
                self.file_list.addItem(item)
        except PermissionError:
            self.file_list.addItem("Permission denied")
        self.path_display.setText(self.current_path)

    def item_double_clicked(self, item):
        path = os.path.join(self.current_path, item.text())
        if os.path.isdir(path):
            self.current_path = path
            self.update_file_list()

    def go_up(self):
        self.current_path = os.path.dirname(self.current_path)
        self.update_file_list()

    def select_file(self):
        if self.file_list.currentItem():
            self.selected_file = os.path.join(self.current_path, self.file_list.currentItem().text())
            if not os.path.isdir(self.selected_file):
                self.accept()

class VideoGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Audio file input
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel('Audio File:'))
        self.audio_input = QLineEdit()
        audio_layout.addWidget(self.audio_input)
        audio_button = QPushButton('Browse')
        audio_button.clicked.connect(lambda: self.browse_file(self.audio_input))
        audio_layout.addWidget(audio_button)
        layout.addLayout(audio_layout)

        # Image file input
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel('Image File:'))
        self.image_input = QLineEdit()
        image_layout.addWidget(self.image_input)
        image_button = QPushButton('Browse')
        image_button.clicked.connect(lambda: self.browse_file(self.image_input))
        image_layout.addWidget(image_button)
        layout.addLayout(image_layout)

        # Heading text input
        heading_layout = QHBoxLayout()
        heading_layout.addWidget(QLabel('Heading Text:'))
        self.heading_input = QLineEdit()
        heading_layout.addWidget(self.heading_input)
        layout.addLayout(heading_layout)

        # Font input
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel('Font:'))
        self.font_input = QLineEdit()
        self.font_input.setText('Arial')
        font_layout.addWidget(self.font_input)
        layout.addLayout(font_layout)

        # Color inputs
        self.heading_color = '#FFFFFF'
        self.outline_color = '#000000'
        self.wave_color = '#FF0000'

        heading_color_layout = QHBoxLayout()
        heading_color_layout.addWidget(QLabel('Heading Color:'))
        self.heading_color_button = QPushButton(self.heading_color)
        self.heading_color_button.clicked.connect(lambda: self.choose_color('heading'))
        heading_color_layout.addWidget(self.heading_color_button)
        layout.addLayout(heading_color_layout)

        outline_color_layout = QHBoxLayout()
        outline_color_layout.addWidget(QLabel('Outline Color:'))
        self.outline_color_button = QPushButton(self.outline_color)
        self.outline_color_button.clicked.connect(lambda: self.choose_color('outline'))
        outline_color_layout.addWidget(self.outline_color_button)
        layout.addLayout(outline_color_layout)

        wave_color_layout = QHBoxLayout()
        wave_color_layout.addWidget(QLabel('Wave Color:'))
        self.wave_color_button = QPushButton(self.wave_color)
        self.wave_color_button.clicked.connect(lambda: self.choose_color('wave'))
        wave_color_layout.addWidget(self.wave_color_button)
        layout.addLayout(wave_color_layout)

        # Output file input
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel('Output File:'))
        self.output_input = QLineEdit()
        self.output_input.setText('output.mp4')
        output_layout.addWidget(self.output_input)
        output_button = QPushButton('Browse')
        output_button.clicked.connect(lambda: self.browse_file(self.output_input))
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        # Generate button
        self.generate_button = QPushButton('Generate Video')
        self.generate_button.clicked.connect(self.generate_video)
        layout.addWidget(self.generate_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.setWindowTitle('Video Generator')
        self.show()

    def browse_file(self, input_field):
        dialog = CustomFileBrowser(self)
        if dialog.exec_() == QDialog.Accepted:
            input_field.setText(dialog.selected_file)

    def choose_color(self, color_type):
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            if color_type == 'heading':
                self.heading_color = color_hex
                self.heading_color_button.setText(color_hex)
            elif color_type == 'outline':
                self.outline_color = color_hex
                self.outline_color_button.setText(color_hex)
            elif color_type == 'wave':
                self.wave_color = color_hex
                self.wave_color_button.setText(color_hex)

    def generate_video(self):
        params = {
            'audio_path': self.audio_input.text(),
            'image_path': self.image_input.text(),
            'heading_text': self.heading_input.text(),
            'font': self.font_input.text(),
            'heading_color': self.heading_color,
            'outline_color': self.outline_color,
            'wave_color': self.wave_color,
            'output_path': self.output_input.text()
        }

        self.generate_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_output.clear()

        self.thread = VideoGeneratorThread(params)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.log_update.connect(self.update_log)
        self.thread.finished.connect(self.generation_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_output.append(message)

    def generation_finished(self):
        self.generate_button.setEnabled(True)
        self.log_output.append("Video generation completed!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoGeneratorGUI()
    sys.exit(app.exec_())