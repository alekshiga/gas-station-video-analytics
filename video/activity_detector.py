import cv2


class ActivityDetector:
    def __init__(self):
        self.prev_frames = {}

    def detect(self, frame, zones):
        events = []
        active_zones = []

        for i, zone in enumerate(list(zones)):
            x, y, w, h = zone

            if w <= 0 or h <= 0:
                continue

            roi = frame[y:y + h, x:x + w]
            if roi.size == 0:
                continue

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if i not in self.prev_frames:
                self.prev_frames[i] = gray
                continue

            delta = cv2.absdiff(self.prev_frames[i], gray)
            thresh = cv2.threshold(delta, 10, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            motion_detected = False

            for c in contours:
                if cv2.contourArea(c) > 200:
                    motion_detected = True
                    cv2.drawContours(roi, [c], -1, (0, 0, 255), 2)

            if motion_detected:
                events.append(f"Движение в зоне {i}")
                active_zones.append(i)

                overlay = frame.copy()
                cv2.rectangle(
                    overlay,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    -1
                )
                frame[:] = cv2.addWeighted(
                    overlay, 0.3,
                    frame, 0.7,
                    0
                )

            self.prev_frames[i] = gray

        return events, active_zones