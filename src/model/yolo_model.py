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

    def start_camera(self):
        """Mở camera."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Cannot open camera")

    def stop_camera(self):
        """Dừng camera."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def detect_lanes(self, frame):
        """Phát hiện làn đường bằng Hough Transform."""
        # Chuyển sang grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Làm mờ để giảm nhiễu
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # Phát hiện cạnh
        edges = cv2.Canny(blur, 50, 150)
        # Tạo mask để chỉ xét vùng dưới của khung hình (nơi có làn đường)
        height, width = frame.shape[:2]
        mask = np.zeros_like(edges)
        polygon = np.array([[(0, height), (width, height), (width, height//2), (0, height//2)]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        masked_edges = cv2.bitwise_and(edges, mask)
        # Hough Transform để tìm đường thẳng
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=100)
        lane_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                lane_lines.append((x1, y1, x2, y2))
        return lane_lines

    def draw_lanes(self, frame, lane_lines):
        """Vẽ làn đường lên frame."""
        lane_frame = frame.copy()
        if lane_lines:
            for x1, y1, x2, y2 in lane_lines:
                cv2.line(lane_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return lane_frame

    def check_violation(self, results, lane_lines):
        """Kiểm tra xe đi sai làn."""
        violations = []
        if not lane_lines:
            return violations
        # Giả định làn đường chia thành 3 vùng (trái, giữa, phải) theo chiều ngang
        frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        lane_width = frame_width / 3
        lane_regions = [
            (0, lane_width, 1),  # Làn trái
            (lane_width, 2 * lane_width, 2),  # Làn giữa
            (2 * lane_width, frame_width, 3)  # Làn phải
        ]
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            for box, label in zip(boxes, labels):
                if label in [2, 3, 5, 7]:  # Ô tô, xe tải, xe buýt, xe máy
                    x_center = (box[0] + box[2]) / 2
                    # Kiểm tra xe nằm ở làn nào
                    for x_min, x_max, lane_id in lane_regions:
                        if x_min <= x_center <= x_max:
                            # Giả định: Ô tô chỉ được đi làn giữa hoặc phải
                            if label == 2 and lane_id == 1:  # Ô tô ở làn trái
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
        """Lấy và xử lý frame từ camera với YOLO và phát hiện làn đường."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Phát hiện phương tiện
                results = self.model.predict(source=frame, save=False)
                annotated_frame = results[0].plot()
                # Phát hiện làn đường
                self.lane_lines = self.detect_lanes(frame)
                # Vẽ làn đường
                final_frame = self.draw_lanes(annotated_frame, self.lane_lines)
                # Kiểm tra vi phạm
                violations = self.check_violation(results, self.lane_lines)
                return cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB), violations
        return None, []

    def save_frame(self, frame, image_path):
        """Lưu frame vào file."""
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def is_camera_running(self):
        """Kiểm tra trạng thái camera."""
        return self.cap is not None and self.cap.isOpened()