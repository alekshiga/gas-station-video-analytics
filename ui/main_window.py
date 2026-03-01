from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QPushButton, QTextEdit
)

from video.video_thread import VideoThread
from ui.video_widget import VideoWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Мониторинг АЗС")
        self.setGeometry(100, 100, 1200, 700)

        self.video_thread = VideoThread()

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        self.video_widget = VideoWidget()
        main_layout.addWidget(self.video_widget, 3)

        right_panel = QVBoxLayout()

        self.start_btn = QPushButton("Старт")
        self.stop_btn = QPushButton("Стоп")
        self.clear_btn = QPushButton("Очистить зоны")

        right_panel.addWidget(self.start_btn)
        right_panel.addWidget(self.stop_btn)
        right_panel.addWidget(self.clear_btn)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        right_panel.addWidget(self.log_widget)

        main_layout.addLayout(right_panel, 1)

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.clear_btn.clicked.connect(self.clear_zones)

        self.video_thread.frame_ready.connect(self.video_widget.set_frame)
        self.video_thread.log_signal.connect(self.add_log)

        # Сигнал добавления зоны
        self.video_widget.zone_added.connect(self.on_zones_updated)

    def start_camera(self):
        if not self.video_thread.isRunning():
            self.video_thread.update_zones(self.video_widget.zones)
            self.video_thread.start()

    def stop_camera(self):
        if self.video_thread.isRunning():
            self.video_thread.stop()

    def clear_zones(self):
        self.video_widget.zones.clear()
        self.video_thread.update_zones(self.video_widget.zones)
        self.video_widget.update()

    def on_zones_updated(self, zones):
        if self.video_widget.frame_width == 0:
            return

        label_w = self.video_widget.width()
        label_h = self.video_widget.height()

        frame_w = self.video_widget.frame_width
        frame_h = self.video_widget.frame_height

        scale_x = frame_w / label_w
        scale_y = frame_h / label_h

        scaled_zones = []

        for x, y, w, h in zones:
            scaled_zones.append((
                int(x * scale_x),
                int(y * scale_y),
                int(w * scale_x),
                int(h * scale_y)
            ))

        print("Масштабированные зоны:", scaled_zones)
        self.video_thread.update_zones(scaled_zones)

    def add_log(self, text):
        self.log_widget.append(text)