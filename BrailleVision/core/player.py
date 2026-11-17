
import time
import threading

from PySide6.QtCore import QThread, Signal
from core.braille import BrailleConverter


class VideoPlayer(QThread):
    frame_ready = Signal(object)
    playback_finished = Signal()

    def __init__(self, video_reader):
        super().__init__()

        self.video = video_reader

        self.converter = BrailleConverter(
            columns=120,
            contrast=2.0,
            sharpen=True,
            invert=False
        )

        source_fps = (
            self.video.fps
            if self.video.fps > 0
            else 30
        )

        self.target_fps = min(source_fps, 24)
        self.interval = 1.0 / self.target_fps

        self.skip_ratio = (
            source_fps / self.target_fps - 1
        )

        self.skip_accumulator = 0

        self.running = True
        self.paused = threading.Event()

    def set_columns(self, columns):
        self.converter.columns = columns

    def play(self):
        if self.isRunning():
            self.paused.clear()
        else:
            self.running = True
            self.paused.clear()
            self.start()

    def pause(self):
        self.paused.set()

    def stop(self):
        self.running = False
        self.paused.clear()

        if self.isRunning():
            self.wait()

    def run(self):
        while self.running:
            if self.paused.is_set():
                time.sleep(0.01)
                continue

            start = time.perf_counter()

            frame = self.video.read_frame()

            if frame is None:
                break

            result = self.converter.convert(frame)

            self.frame_ready.emit(result)

            # Bỏ qua frame khi nguồn có FPS cao
            self.skip_accumulator += self.skip_ratio

            while self.skip_accumulator >= 1:
                skipped = self.video.read_frame()

                if skipped is None:
                    self.running = False
                    break

                self.skip_accumulator -= 1

            # Giữ nhịp phát mục tiêu
            elapsed = time.perf_counter() - start
            remaining = self.interval - elapsed

            if remaining > 0:
                time.sleep(remaining)

        self.playback_finished.emit()
