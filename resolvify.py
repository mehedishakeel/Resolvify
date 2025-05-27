import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton,
    QLabel, QVBoxLayout, QWidget, QComboBox, QListWidget,
    QMessageBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont

class DragDropList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DropOnly)
        self.setStyleSheet("""
            background-color: #202124;
            color: white;
            font-size: 18px;
            border: 2px dashed #4caf50;
            border-radius: 10px;
            padding: 10px;
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                if os.path.isfile(filepath):
                    self.addItem(filepath)
            event.acceptProposedAction()
        else:
            event.ignore()

class Resolvify(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resolvify")
        self.setFixedSize(800, 600)  # Bigger window
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.output_dir = os.path.expanduser("~/Videos")

        self.file_list = DragDropList()
        self.file_list.setFixedHeight(250)  # Bigger list view height

        self.combo = QComboBox()
        self.combo.addItems([
            "MKV to WAV (Resolve)",
            "MP4 to WAV (Resolve)",
            "MP4 to MOV (ProRes) (Resolve)",
            "MKV to MP4 (H.264)",
            "MP4 to MP3",
            "WAV to MP3"
        ])
        self.combo.setStyleSheet("""
            background-color: #303134;
            color: white;
            font-size: 18px;
            padding: 8px;
            border-radius: 8px;
        """)

        self.output_label = QLabel(f"Output Directory: {self.output_dir}")
        self.output_label.setStyleSheet("color: white; font-size: 18px;")

        # Buttons with bigger size & hover effects
        button_style = """
            QPushButton {
                font-size: 20px;
                padding: 12px 20px;
                background-color: #4caf50;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        self.select_output_btn = QPushButton("📁 Select Output Directory")
        self.select_output_btn.setStyleSheet(button_style)
        self.add_files_btn = QPushButton("➕ Add Files")
        self.add_files_btn.setStyleSheet(button_style)
        self.convert_btn = QPushButton("🚀 Convert Files")
        self.convert_btn.setStyleSheet(button_style)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(30)
        self.progress.setStyleSheet("""
            QProgressBar {
                text-align: center;
                color: black;
                background-color: #303134;
                border-radius: 15px;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 15px;
            }
        """)

        layout = QVBoxLayout()

        title_label = QLabel("🎞️ Drag and Drop OBS Recordings Below or Click 'Add Files':")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 22px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        layout.addWidget(self.file_list)
        layout.addWidget(self.add_files_btn)

        conversion_label = QLabel("🛠️ Choose Conversion Type:")
        conversion_label.setStyleSheet("color: white; font-size: 16px; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(conversion_label)
        layout.addWidget(self.combo)
        layout.addWidget(self.output_label)
        layout.addWidget(self.select_output_btn)

        # Put convert button and progress bar side by side
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.convert_btn, 3)
        bottom_layout.addWidget(self.progress, 7)
        bottom_layout.setSpacing(15)
        layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.set_dark_palette()

        # Connect signals
        self.select_output_btn.clicked.connect(self.select_output_directory)
        self.convert_btn.clicked.connect(self.convert_files)
        self.add_files_btn.clicked.connect(self.add_files)

    def set_dark_palette(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Highlight, QColor(76, 175, 80))  # green highlight
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.instance().setPalette(dark_palette)

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir)
        if directory:
            self.output_dir = directory
            self.output_label.setText(f"Output Directory: {self.output_dir}")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "Video and Audio Files (*.mkv *.mp4 *.wav)"
        )
        for file in files:
            self.file_list.addItem(file)

    def convert_files(self):
        conversion_type = self.combo.currentText()
        total_files = self.file_list.count()
        if total_files == 0:
            QMessageBox.warning(self, "No Files", "Please add at least one file.")
            return

        self.convert_btn.setEnabled(False)
        self.select_output_btn.setEnabled(False)
        self.add_files_btn.setEnabled(False)
        self.progress.setValue(0)

        completed = 0
        for i in range(total_files):
            filepath = self.file_list.item(i).text()
            filename = os.path.basename(filepath)
            name, ext = os.path.splitext(filename)
            ext = ext.lower()

            cmd = None
            output_path = None

            if conversion_type == "MKV to WAV (Resolve)" and ext == ".mkv":
                output_path = os.path.join(self.output_dir, f"{name}.wav")
                cmd = ["ffmpeg", "-i", filepath, "-vn", "-acodec", "pcm_s16le", output_path]

            elif conversion_type == "MP4 to WAV (Resolve)" and ext == ".mp4":
                output_path = os.path.join(self.output_dir, f"{name}.wav")
                cmd = ["ffmpeg", "-i", filepath, "-vn", "-acodec", "pcm_s16le", output_path]

            elif conversion_type == "MP4 to MOV (ProRes) (Resolve)" and ext == ".mp4":
                output_path = os.path.join(self.output_dir, f"{name}_prores.mov")
                cmd = [
                    "ffmpeg", "-i", filepath,
                    "-c:v", "prores_ks", "-profile:v", "3", "-qscale:v", "9",
                    "-c:a", "pcm_s16le",
                    output_path
                ]

            elif conversion_type == "MKV to MP4 (H.264)" and ext == ".mkv":
                output_path = os.path.join(self.output_dir, f"{name}.mp4")
                cmd = ["ffmpeg", "-i", filepath, "-c:v", "libx264", "-c:a", "aac", output_path]

            elif conversion_type == "MP4 to MP3" and ext == ".mp4":
                output_path = os.path.join(self.output_dir, f"{name}.mp3")
                cmd = ["ffmpeg", "-i", filepath, "-q:a", "0", "-map", "a", output_path]

            elif conversion_type == "WAV to MP3" and ext == ".wav":
                output_path = os.path.join(self.output_dir, f"{name}.mp3")
                cmd = ["ffmpeg", "-i", filepath, "-q:a", "0", output_path]

            else:
                continue

            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            completed += 1
            progress_percent = int((completed / total_files) * 100)
            self.progress.setValue(progress_percent)

        self.convert_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.add_files_btn.setEnabled(True)

        QMessageBox.information(self, "Conversion Complete", "All files converted successfully!")

if __name__ == "__main__":
    if sys.platform != "linux":
        print("This application is for Linux systems only.")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = Resolvify()
    window.show()
    sys.exit(app.exec_())

