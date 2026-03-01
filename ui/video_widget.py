import cv2
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QRect, pyqtSignal


class VideoWidget(QLabel):
    zone_added = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.current_pixmap = None
        self.zones = []
        self.active_zones = []

        self.drawing = False
        self.start_point = None
        self.end_point = None

        self.frame_width = 0
        self.frame_height = 0

    def set_frame(self, frame, active_zones):
        self.active_zones = active_zones

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape

        # Сохраняем реальные размеры кадра
        self.frame_width = w
        self.frame_height = h

        bytes_per_line = ch * w

        image = QImage(
            rgb.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        ).copy()  # важно!

        self.current_pixmap = QPixmap.fromImage(image)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.current_pixmap:
            painter.drawPixmap(self.rect(), self.current_pixmap)

        for i, zone in enumerate(self.zones):
            rect = QRect(*zone)

            if i in self.active_zones:
                pen = QPen(Qt.GlobalColor.red, 3)
            else:
                pen = QPen(Qt.GlobalColor.green, 2)

            painter.setPen(pen)
            painter.drawRect(rect)

        if self.drawing and self.start_point and self.end_point:
            pen = QPen(Qt.GlobalColor.yellow, 2)
            painter.setPen(pen)
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.end_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            rect = QRect(self.start_point, self.end_point).normalized()

            zone = (rect.x(), rect.y(), rect.width(), rect.height())
            self.zones.append(zone)

            print("Добавлена зона:", zone)

            # Уведомляем главное окно
            self.zone_added.emit(self.zones)

            self.update()