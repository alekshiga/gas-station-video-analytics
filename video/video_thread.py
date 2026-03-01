import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from video.activity_detector import ActivityDetector


class VideoThread(QThread):
    frame_ready = pyqtSignal(object, object)
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        self.zones = []
        self.detector = ActivityDetector()

    def update_zones(self, zones):
        self.zones = zones.copy()
        print("Текущие зоны в потоке:", self.zones)

    def run(self):
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("Камера не открылась")
            return

        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            events, active_zones = self.detector.detect(frame, self.zones)

            for e in events:
                self.log_signal.emit(e)

            self.frame_ready.emit(frame.copy(), active_zones)

        self.cap.release()

    def stop(self):
        self.running = False
        self.wait()