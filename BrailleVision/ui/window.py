
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt

from core.video import VideoReader
from core.player import VideoPlayer
from ui.renderer import BrailleRenderer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BrailleVision - Colored Braille")
        self.resize(1000, 700)

        self.video = None
        self.player = None

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        self.info = QLabel("No video selected")
        layout.addWidget(self.info)

        self.renderer = BrailleRenderer()

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.renderer)
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.scroll)

        buttons = QHBoxLayout()

        open_btn = QPushButton("Open Video")
        play_btn = QPushButton("Play")
        pause_btn = QPushButton("Pause")

        buttons.addWidget(open_btn)
        buttons.addWidget(play_btn)
        buttons.addWidget(pause_btn)

        layout.addLayout(buttons)

        open_btn.clicked.connect(self.open_video)
        play_btn.clicked.connect(self.play_video)
        pause_btn.clicked.connect(self.pause_video)

    def open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov)"
        )

        if not path:
            return

        try:
            if self.player:
                self.player.stop()
                try:
                    self.renderer.columns_changed.disconnect(
                        self.player.set_columns
                    )
                except (TypeError, RuntimeError):
                    pass

            if self.video:
                self.video.release()

            self.video = VideoReader(path)
            self.player = VideoPlayer(self.video)

            self.renderer.set_source_size(
                self.video.width,
                self.video.height
            )

            self.player.set_columns(
                self.renderer.columns
            )

            self.renderer.columns_changed.connect(
                self.player.set_columns
            )

            self.player.frame_ready.connect(
                self.renderer.render
            )

            self.info.setText(
                f"{self.video.width}x{self.video.height} | "
                f"{self.video.fps:.2f} FPS | "
                f"{self.video.total_frames} frames"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def play_video(self):
        if self.player:
            self.player.play()

    def pause_video(self):
        if self.player:
            self.player.pause()

    def closeEvent(self, event):
        if self.player:
            self.player.stop()

        if self.video:
            self.video.release()

        event.accept()
