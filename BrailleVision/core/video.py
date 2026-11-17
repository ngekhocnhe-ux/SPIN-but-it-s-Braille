
import cv2


class VideoReader:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)

        if not self.cap.isOpened():
            raise ValueError("Cannot open video: " + path)

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def read_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
