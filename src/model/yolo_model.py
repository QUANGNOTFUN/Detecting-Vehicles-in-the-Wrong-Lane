import cv2
import numpy as np
from ultralytics import YOLO
import os
import datetime

class YoloModel:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.cap = None
        self.lane_lines = None
        self.video_path = None  # New attribute for video file path
        self.is_video = False  # Flag to indicate video file mode

    def start_camera(self, video_path=None):
        """Mở camera hoặc video file."""
        self.stop_camera()  # Ensure any existing capture is stopped
        self.video_path = video_path
        self.is_video = video_path is not None

        if self.is_video:
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open video file: {video_path}")
        else:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Cannot open camera")

    def stop_camera(self):
        """Dừng camera hoặc video."""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_path = None
        self.is_video = False

    def detect_lanes(self, frame):
        # Unchanged
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        height, width = frame.shape[:2]
        mask = np.zeros_like(edges)
        polygon = np.array([[(0, height), (width, height), (width, height//2), (0, height//2)]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=100)
        lane_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                lane_lines.append((x1, y1, x2, y2))
        return lane_lines

    def draw_lanes(self, frame, lane_lines):
        # Unchanged
        lane_frame = frame.copy()
        if lane_lines:
            for x1, y1, x2, y2 in lane_lines:
                cv2.line(lane_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return lane_frame

    def check_violation(self, results, lane_lines):
        # Unchanged
        violations = []
        if not lane_lines:
            return violations
        frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) if self.cap else 640
        lane_width = frame_width / 3
        lane_regions = [
            (0, lane_width, 1),
            (lane_width, 2 * lane_width, 2),
            (2 * lane_width, frame_width, 3)
        ]
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            for box, label in zip(boxes, labels):
                if label in [2, 3, 5, 7]:
                    x_center = (box[0] + box[2]) / 2
                    for x_min, x_max, lane_id in lane_regions:
                        if x_min <= x_center <= x_max:
                            if label == 2 and lane_id == 1:
                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                image_path = f"frames/frame_{timestamp.replace(':', '-')}.jpg"
                                violations.append({
                                    "timestamp": timestamp,
                                    "vehicle_type": "Ô tô",
                                    "lane_id": lane_id,
                                    "image_path": image_path
                                })
                            break
        return violations

    def get_frame(self):
        # Unchanged
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                results = self.model.predict(source=frame, save=False)
                annotated_frame = results[0].plot()
                self.lane_lines = self.detect_lanes(frame)
                final_frame = self.draw_lanes(annotated_frame, self.lane_lines)
                violations = self.check_violation(results, self.lane_lines)
                return cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB), violations
        return None, []

    def save_frame(self, frame, image_path):
        # Unchanged
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def is_camera_running(self):
        """Kiểm tra trạng thái camera hoặc video."""
        return self.cap is not None and self.cap.isOpened()