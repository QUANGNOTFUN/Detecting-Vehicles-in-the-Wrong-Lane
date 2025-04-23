import cv2
import numpy as np
from ultralytics import YOLO
import json
import os
import datetime
from typing import List, Dict, Tuple, Optional

class LaneDetector:
    def __init__(self, hsv_lower: np.ndarray, hsv_upper: np.ndarray, hough_params: Dict):
        """
            hsv_lower (np.ndarray): Giá trị HSV tối thiểu để phân đoạn đường.
            hsv_upper (np.ndarray): Giá trị HSV tối đa để phân đoạn đường.
            hough_params (Dict): Tham số cho thuật toán Hough Transform.
        """
        self.hsv_lower = hsv_lower
        self.hsv_upper = hsv_upper
        self.hough_params = hough_params

    def segment_road(self, frame: np.ndarray, results: List, vehicle_classes: List[int]) -> np.ndarray:
        """
        Phân đoạn khu vực đường dựa trên hộp giới hạn phương tiện và màu sắc HSV.
        Tham số:
            frame (np.ndarray): Khung hình đầu vào.
            results (List): Kết quả dự đoán từ YOLO.
            vehicle_classes (List[int]): Danh sách nhãn lớp phương tiện.
        Trả về:
            np.ndarray: Mask của khu vực đường.
        """
        road_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            for box, label in zip(boxes, labels):
                if label in vehicle_classes:
                    x1, y1, x2, y2 = box.astype(int)
                    road_mask[y1:y2, x1:x2] = 255

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_road_mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
        road_mask = cv2.bitwise_or(road_mask, color_road_mask)
        road_mask = cv2.morphologyEx(road_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        return road_mask

    def detect_lanes(self, frame: np.ndarray, results: List, vehicle_classes: List[int]) -> List[Tuple]:
        """
        Phát hiện các vạch kẻ đường bằng thuật toán Canny và Hough Transform.
        Tham số:
            frame (np.ndarray): Khung hình đầu vào.
            results (List): Kết quả dự đoán từ YOLO.
            vehicle_classes (List[int]): Danh sách nhãn lớp phương tiện.
        Trả về:
            List[Tuple]: Danh sách các đường thẳng (x1, y1, x2, y2) đại diện cho vạch kẻ.
        """
        road_mask = self.segment_road(frame, results, vehicle_classes)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)
        masked_edges = cv2.bitwise_and(edges, road_mask)
        lines = cv2.HoughLinesP(
            masked_edges, 1, np.pi/180,
            threshold=self.hough_params["threshold"],
            minLineLength=self.hough_params["minLineLength"],
            maxLineGap=self.hough_params["maxLineGap"]
        )
        lane_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(x2 - x1) > 20 or abs(y2 - y1) > 20:
                    lane_lines.append((x1, y1, x2, y2))
        return lane_lines

class LicensePlateDetector:
    def __init__(self, ocr_lang: str = "en", license_plate_label: int = 80):
        """
        Khởi tạo bộ phát hiện và đọc biển số xe.
        Tham số:
            ocr_lang (str): Ngôn ngữ cho PaddleOCR (mặc định: "en").
            license_plate_label (int): Nhãn lớp cho biển số xe (mặc định: 80).
        """
        self.license_plate_label = license_plate_label
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang=ocr_lang, show_log=False)
        except Exception as e:
            print(f"Cảnh báo: Khởi tạo PaddleOCR thất bại: {e}")
            self.ocr = None

    def detect_license_plates(self, frame: np.ndarray, results: List, threshold: float) -> List[Dict]:
        """
        Phát hiện và đọc biển số xe từ khung hình.
        Tham số:
            frame (np.ndarray): Khung hình đầu vào.
            results (List): Kết quả dự đoán từ YOLO.
            threshold (float): Ngưỡng độ tin cậy để lọc đối tượng.
        Trả về:
            List[Dict]: Danh sách các biển số (vị trí, văn bản, độ tin cậy).
        """
        license_plates = []
        if self.ocr is None:
            return license_plates
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, label, conf in zip(boxes, labels, confidences):
                if conf < threshold or label != self.license_plate_label:
                    continue
                try:
                    x1, y1, x2, y2 = box.astype(int)
                    plate_img = frame[y1:y2, x1:x2]
                    if plate_img.size == 0:
                        continue
                    plate_img_rgb = cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB)
                    ocr_result = self.ocr.ocr(plate_img_rgb, cls=True)
                    plate_text = ""
                    if ocr_result and ocr_result[0]:
                        for line in ocr_result[0]:
                            plate_text += line[1][0] + " "
                    license_plates.append({
                        "box": (x1, y1, x2, y2),
                        "text": plate_text.strip(),
                        "confidence": conf
                    })
                except Exception as e:
                    print(f"Lỗi khi xử lý biển số: {e}")
                    continue
        return license_plates

class YoloModel:
    def __init__(self, model_path: str, config_path: Optional[str] = None):
        """
        Khởi tạo mô hình YOLO để phát hiện phương tiện, làn đường, và biển số.
        Tham số:
            model_path (str): Đường dẫn đến file trọng số YOLO.
            config_path (Optional[str]): Đường dẫn đến file JSON cấu hình (mặc định: None).
        """
        self.model = YOLO(model_path)
        self.cap = None
        self.video_path = None
        self.is_video = False
        # Cấu hình mặc định
        self.detection_threshold = 0.5
        self.lane_config = []
        self.vehicle_classes = [1, 2, 3, 5, 7]  # Xe đạp, ô tô, xe máy, xe buýt, xe tải
        self.lane_detector = LaneDetector(
            hsv_lower=np.array([0, 0, 50]),
            hsv_upper=np.array([180, 50, 200]),
            hough_params={"threshold": 50, "minLineLength": 50, "maxLineGap": 100}
        )
        self.plate_detector = LicensePlateDetector(license_plate_label=80)
        # Tải cấu hình JSON nếu có
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str) -> None:
        """
        Tải cấu hình từ file JSON hoặc giữ nguyên mặc định nếu lỗi.
        Tham số:
            config_path (str): Đường dẫn đến file JSON.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.detection_threshold = config.get("detection_threshold", self.detection_threshold)
            self.lane_config = config.get("lanes", self.lane_config)
            num_lanes = config.get("num_lanes", len(self.lane_config))
            if num_lanes != len(self.lane_config):
                print(f"Cảnh báo: num_lanes ({num_lanes}) không khớp với số làn trong config ({len(self.lane_config)})")
            self.vehicle_classes = config.get("vehicle_classes", self.vehicle_classes)
            hsv_config = config.get("hsv", {
                "lower": [0, 0, 50],
                "upper": [180, 50, 200]
            })
            hough_params = config.get("hough_params", {
                "threshold": 50,
                "minLineLength": 50,
                "maxLineGap": 100
            })
            self.lane_detector = LaneDetector(
                hsv_lower=np.array(hsv_config.get("lower", [0, 0, 50])),
                hsv_upper=np.array(hsv_config.get("upper", [180, 50, 200])),
                hough_params=hough_params
            )
            self.plate_detector = LicensePlateDetector(
                license_plate_label=config.get("license_plate_label", 80)
            )
            print(f"Đã tải cấu hình từ {config_path}")
        except Exception as e:
            print(f"Lỗi khi tải lane_config.json: {e}. Sử dụng cấu hình mặc định.")

    def reload_config(self, config_path: str) -> None:
        """
        Tải lại cấu hình từ file JSON khi có thay đổi.
        Tham số:
            config_path (str): Đường dẫn đến file JSON.
        """
        self.load_config(config_path)

    def start_camera(self, video_path: Optional[str] = None) -> None:
        """
        Mở luồng video hoặc webcam.
        Tham số:
            video_path (Optional[str]): Đường dẫn đến file video (mặc định: None để dùng webcam).
        """
        self.stop_camera()
        self.video_path = video_path
        self.is_video = video_path is not None
        try:
            self.cap = cv2.VideoCapture(video_path if self.is_video else 0)
            if not self.cap.isOpened():
                raise Exception(f"Không thể mở {'video' if self.is_video else 'webcam'}")
        except Exception as e:
            print(f"Lỗi: {e}")
            raise

    def stop_camera(self) -> None:
        """
        Đóng luồng video hoặc webcam.
        """
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_path = None
        self.is_video = False

    def check_violation(self, results: List, lane_lines: List, license_plates: List[Dict]) -> List[Dict]:
        """
        Kiểm tra vi phạm giao thông (phương tiện đi sai làn).
        Tham số:
            results (List): Kết quả dự đoán từ YOLO.
            lane_lines (List): Danh sách vạch kẻ đường.
            license_plates (List[Dict]): Danh sách biển số xe.
        Trả về:
            List[Dict]: Danh sách các vi phạm (thời gian, loại phương tiện, biển số, v.v.).
        """
        violations = []
        if not lane_lines or not self.lane_config:
            return violations
        frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) if self.cap else 426
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, label, conf in zip(boxes, labels, confidences):
                if conf < self.detection_threshold or label not in self.vehicle_classes:
                    continue
                x_center = (box[0] + box[2]) / 2
                for lane in self.lane_config:
                    if lane["x_min"] <= x_center <= lane["x_max"]:
                        if label not in lane["allowed_vehicles"]:
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            image_path = f"frames/frame_{timestamp.replace(':', '-')}.jpg"
                            vehicle_type = {
                                1: "Xe đạp", 2: "Ô tô", 3: "Xe máy",
                                5: "Xe buýt", 7: "Xe tải"
                            }.get(label, "Không xác định")
                            plate_text = "Không xác định"
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
                                "x_center": x_center
                            })
                        break
        return violations

    def draw_elements(self, frame: np.ndarray, results: List, lane_lines: List,
                     license_plates: List, violations: List) -> np.ndarray:
        """
        Vẽ vạch kẻ đường, hộp giới hạn, và nhãn lên khung hình.
        Tham số:
            frame (np.ndarray): Khung hình đầu vào.
            results (List): Kết quả dự đoán từ YOLO.
            lane_lines (List): Danh sách vạch kẻ đường.
            license_plates (List): Danh sách biển số xe.
            violations (List): Danh sách vi phạm.
        Trả về:
            np.ndarray: Khung hình với các yếu tố được vẽ.
        """
        frame_with_lanes = frame.copy()
        for x1, y1, x2, y2 in lane_lines:
            cv2.line(frame_with_lanes, (x1, y1), (x2, y2), (0, 0, 255), 2)
        violation_plates = {v["license_plate"] for v in violations}
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, label, conf in zip(boxes, labels, confidences):
                if conf < self.detection_threshold or label not in self.vehicle_classes:
                    continue
                x1, y1, x2, y2 = box.astype(int)
                plate_text = "Không xác định"
                for plate in license_plates:
                    px1, py1, px2, py2 = plate["box"]
                    if px1 >= x1 and px2 <= x2 and py1 >= y1 and py2 <= y2:
                        plate_text = plate["text"]
                        break
                color = (255, 0, 0) if plate_text in violation_plates else (0, 255, 0)
                cv2.rectangle(frame_with_lanes, (x1, y1), (x2, y2), color, 2)
                vehicle_type = {
                    1: "Xe đạp", 2: "Ô tô", 3: "Xe máy",
                    5: "Xe buýt", 7: "Xe tải"
                }.get(label, "Không xác định")
                cv2.putText(frame_with_lanes, f"{vehicle_type} - {plate_text}",
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame_with_lanes

    def get_frame(self) -> Tuple[Optional[np.ndarray], List[Dict]]:
        """
        Xử lý khung hình và trả về khung hình đã vẽ cùng danh sách vi phạm.
        Trả về:
            Tuple[Optional[np.ndarray], List[Dict]]: Khung hình và danh sách vi phạm.
        """
        if not self.is_camera_running():
            return None, []
        try:
            ret, frame = self.cap.read()
            if not ret:
                return None, []
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model.predict(source=frame, save=False)
            lane_lines = self.lane_detector.detect_lanes(frame, results, self.vehicle_classes)
            license_plates = self.plate_detector.detect_license_plates(frame, results, self.detection_threshold)
            violations = self.check_violation(results, lane_lines, license_plates)
            frame_with_elements = self.draw_elements(frame_rgb, results, lane_lines, license_plates, violations)
            return frame_with_elements, violations
        except Exception as e:
            print(f"Lỗi khi xử lý khung hình: {e}")
            return None, []

    def save_frame(self, frame: np.ndarray, image_path: str) -> None:
        """
        Lưu khung hình vào file.
        Tham số:
            frame (np.ndarray): Khung hình cần lưu.
            image_path (str): Đường dẫn đến file lưu.
        """
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def is_camera_running(self) -> bool:
        """
        Kiểm tra trạng thái camera/video.
        Trả về:
            bool: True nếu camera đang chạy, False nếu không.
        """
        return self.cap is not None and self.cap.isOpened()