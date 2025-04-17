import cv2
import numpy as np
from ultralytics import YOLO
import os
import datetime
from paddleocr import PaddleOCR

class YoloModel:
    def update_button_states(self, running):
        return {
            "start_button": "disabled" if running else "normal",
            "video_button": "disabled" if running else "normal",
            "stop_button": "normal" if running else "disabled"
        }
    def __init__(self, model_path):
        self.model = YOLO(model_path)  # yolov8n.pt (đã huấn luyện để phát hiện biển số)
        self.cap = None
        self.lane_lines = None
        self.video_path = None
        self.is_video = False
        self.lane_config = None
        self.detection_threshold = 0.5
        self.non_vehicle_classes = [0, 1]  # person, bicycle (COCO dataset)
        self.ocr = PaddleOCR(use_angle_cls=True, lang="en")  # Khởi tạo PaddleOCR

    def update_lane_config(self, config_data):
        self.lane_config = config_data["lanes"]
        self.detection_threshold = config_data["detection_threshold"]

    def start_camera(self, video_path=None):
        self.stop_camera()
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
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_path = None
        self.is_video = False

    def segment_road(self, frame, results):
        """Phân đoạn khu vực đường."""
        road_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            for box, label in zip(boxes, labels):
                if label in [2, 3, 5, 7]:  # Xe: coi khu vực xe là một phần của đường
                    x1, y1, x2, y2 = box.astype(int)
                    road_mask[y1:y2, x1:x2] = 255

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_road = np.array([0, 0, 50])
        upper_road = np.array([180, 50, 200])
        color_road_mask = cv2.inRange(hsv, lower_road, upper_road)

        non_road_mask = np.zeros_like(road_mask)
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            for box, label in zip(boxes, labels):
                if label in self.non_vehicle_classes:
                    x1, y1, x2, y2 = box.astype(int)
                    non_road_mask[y1:y2, x1:x2] = 255

        road_mask = cv2.bitwise_or(road_mask, color_road_mask)
        road_mask = cv2.bitwise_and(road_mask, cv2.bitwise_not(non_road_mask))
        road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        return road_mask

    def detect_lanes(self, frame, results):
        road_mask = self.segment_road(frame, results)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        masked_edges = cv2.bitwise_and(edges, road_mask)
        lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=100)
        lane_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(x2 - x1) > 20 or abs(y2 - y1) > 20:
                    lane_lines.append((x1, y1, x2, y2))
        return lane_lines

    def detect_license_plates(self, frame, results):
        """Phát hiện và đọc biển số xe."""
        license_plates = []
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, label, conf in zip(boxes, labels, confidences):
                if conf < self.detection_threshold:
                    continue
                # Giả định label 80 là "license plate" (sau khi huấn luyện)
                if label == 80:
                    x1, y1, x2, y2 = box.astype(int)
                    # Cắt khu vực biển số
                    plate_img = frame[y1:y2, x1:x2]
                    # Chuyển sang định dạng RGB để dùng PaddleOCR
                    plate_img_rgb = cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB)
                    # Đọc ký tự bằng PaddleOCR
                    ocr_result = self.ocr.ocr(plate_img_rgb, cls=True)
                    plate_text = ""
                    if ocr_result and len(ocr_result) > 0:
                        for line in ocr_result[0]:
                            plate_text += line[1][0] + " "
                    license_plates.append({
                        "box": (x1, y1, x2, y2),
                        "text": plate_text.strip(),
                        "confidence": conf
                    })
        return license_plates

    def draw_lanes(self, frame, lane_lines):
        lane_frame = frame.copy()
        if lane_lines:
            for x1, y1, x2, y2 in lane_lines:
                cv2.line(lane_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Đường đỏ
        return lane_frame

    # yolo_model.py
    def check_violation(self, results, lane_lines, license_plates):
        violations = []
        if not lane_lines or not self.lane_config:
            return violations

        frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) if self.cap else 640
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, label, conf in zip(boxes, labels, confidences):
                if conf < self.detection_threshold:
                    continue
                if label not in [2, 3, 5, 7]:
                    continue
                x_center = (box[0] + box[2]) / 2
                for lane in self.lane_config:
                    if lane["x_min"] <= x_center <= lane["x_max"]:
                        if label not in lane["allowed_vehicles"]:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            image_path = f"frames/frame_{timestamp.replace(':', '-')}.jpg"
                            vehicle_type = {2: "Ô tô", 3: "Xe máy", 5: "Xe buýt", 7: "Xe tải"}.get(label, "Unknown")
                            plate_text = "Unknown"
                            for plate in license_plates:
                                px1, py1, px2, py2 = plate["box"]
                                if px1 >= box[0] and px2 <= box[2] and py1 >= box[1] and py2 <= box[3]:
                                    plate_text = plate["text"]
                                    break
                            violations.append({
                                "timestamp": timestamp,
                                "vehicle_type": vehicle_type,
                                "lane_id": lane["lane_id"],
                                "image_path": image_path,
                                "license_plate": plate_text,
                                "x_center": x_center  # Thêm x_center
                            })
                        break
        return violations

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Chuyển khung hình sang RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Dự đoán bằng YOLO
                results = self.model.predict(source=frame, save=False)
                
                # Phát hiện làn đường
                self.lane_lines = self.detect_lanes(frame, results)
                # Vẽ vạch kẻ đường màu đỏ
                frame_with_lanes = self.draw_lanes(frame_rgb, self.lane_lines)
                
                # Kiểm tra vi phạm và vẽ hộp giới hạn
                license_plates = self.detect_license_plates(frame, results)
                violations = self.check_violation(results, self.lane_lines, license_plates)
                
                # Danh sách các phương tiện vi phạm (theo license plate để tránh trùng lặp)
                violation_plates = {v["license_plate"] for v in violations}
                
                # Vẽ hộp giới hạn cho phương tiện
                for result in results:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    labels = result.boxes.cls.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    for box, label, conf in zip(boxes, labels, confidences):
                        if conf < self.detection_threshold:
                            continue
                        # Chỉ vẽ hộp cho các phương tiện (labels 2, 3, 5, 7)
                        if label in [2, 3, 5, 7]:  # Ô tô, xe máy, xe buýt, xe tải
                            x1, y1, x2, y2 = box.astype(int)
                            # Tìm biển số tương ứng với phương tiện
                            plate_text = "Unknown"
                            for plate in license_plates:
                                px1, py1, px2, py2 = plate["box"]
                                if px1 >= x1 and px2 <= x2 and py1 >= y1 and py2 <= y2:
                                    plate_text = plate["text"]
                                    break
                            # Kiểm tra xem phương tiện có vi phạm không
                            if plate_text in violation_plates:
                                color = (0, 0, 255)  # Đỏ cho phương tiện vi phạm
                            else:
                                color = (0, 255, 0)  # Xanh cho phương tiện không vi phạm
                            cv2.rectangle(frame_with_lanes, (x1, y1), (x2, y2), color, 2)
                
                return frame_with_lanes, violations
        return None, []

    def save_frame(self, frame, image_path):
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def is_camera_running(self):
        return self.cap is not None and self.cap.isOpened()