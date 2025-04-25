import cv2
import numpy as np
from ultralytics import YOLO
import os
import datetime
from paddleocr import PaddleOCR
import csv

class YoloModel:
    def __init__(self, model_path, config_view_model):
        self.model = YOLO(model_path)
        self.cap = None
        self.video_path = None
        self.is_video = False
        self.config_view_model = config_view_model
        self.lane_config = None
        self.num_lanes = 0
        self.detection_threshold = 0.5
        self.non_vehicle_classes = [0, 1]
        self.csv_file = "violations/violations.csv"
        self.init_csv()
        self.load_config()
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        except Exception as e:
            print(f"Warning: PaddleOCR initialization failed: {e}")
            self.ocr = None

    def init_csv(self):
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Vehicle Type", "Lane ID", "Image Path", "License Plate", "X Center"])

    def load_config(self):
        config = self.config_view_model.get_config()
        self.lane_config = config["lanes"]
        self.num_lanes = config["num_lanes"]
        self.detection_threshold = config["detection_threshold"]

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

    def detect_license_plates(self, frame, results):
        license_plates = []
        if self.ocr is None:
            return license_plates
            
        for result in results:
            boxes = result.boxes.xyxy.cpu().numpy()
            labels = result.boxes.cls.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            for box, label, conf in zip(boxes, labels, confidences):
                if conf < self.detection_threshold:
                    continue
                if label == 80:
                    try:
                        x1, y1, x2, y2 = box.astype(int)
                        plate_img = frame[y1:y2, x1:x2]
                        if plate_img.size == 0:
                            continue
                        plate_img_rgb = cv2.cvtColor(plate_img, cv2.COLOR_BGR2RGB)
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
                    except Exception as e:
                        print(f"Error processing license plate: {e}")
                        continue
        return license_plates

    def check_violation(self, results, license_plates, frame):
        violations = []
        if not self.lane_config or self.num_lanes <= 0:
            print("Không có lane_config hoặc num_lanes hợp lệ, không thể kiểm tra vi phạm.")
            return violations

        frame_height, frame_width, _ = frame.shape
        print(f"Kích thước khung hình: width={frame_width}, height={frame_height}")

        lane_width = frame_width / self.num_lanes if self.num_lanes > 0 else frame_width

        dynamic_lanes = []
        for i, lane in enumerate(self.lane_config):
            lane_id = lane["lane_id"]
            x_min = i * lane_width
            x_max = (i + 1) * lane_width
            dynamic_lanes.append({
                "lane_id": lane_id,
                "x_min": x_min,
                "x_max": x_max,
                "allowed_vehicles": lane["allowed_vehicles"]
            })
            print(f"Làn {lane_id}: x_min={x_min}, x_max={x_max}, allowed_vehicles={lane['allowed_vehicles']}")

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
                print(f"Phương tiện: label={label}, x_center={x_center}")

                lane_found = False
                for lane in dynamic_lanes:
                    if lane["x_min"] <= x_center <= lane["x_max"]:
                        lane_found = True
                        print(f"Phương tiện nằm trong Làn {lane['lane_id']}: x_min={lane['x_min']}, x_max={lane['x_max']}, allowed_vehicles={lane['allowed_vehicles']}")
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
                            violation = {
                                "timestamp": timestamp,
                                "vehicle_type": vehicle_type,
                                "lane_id": lane["lane_id"],
                                "image_path": image_path,
                                "license_plate": plate_text,
                                "x_center": x_center
                            }
                            violations.append(violation)
                            self.save_violation_to_csv(violation)
                            self.save_frame(frame, image_path)
                        break

                if not lane_found:
                    print(f"Phương tiện không nằm trong làn nào: x_center={x_center}")

        return violations

    def save_violation_to_csv(self, violation):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                violation["timestamp"],
                violation["vehicle_type"],
                violation["lane_id"],
                violation["image_path"],
                violation["license_plate"],
                violation["x_center"]
            ])

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if not ret:
                    return None, []

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.model.predict(source=frame, save=False)
                
                license_plates = self.detect_license_plates(frame, results)
                violations = self.check_violation(results, license_plates, frame_rgb)
                
                violation_plates = {v["license_plate"] for v in violations}
                
                for result in results:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    labels = result.boxes.cls.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    for box, label, conf in zip(boxes, labels, confidences):
                        if conf < self.detection_threshold:
                            continue
                        if label in [2, 3, 5, 7]:
                            x1, y1, x2, y2 = box.astype(int)
                            plate_text = "Unknown"
                            for plate in license_plates:
                                px1, py1, px2, py2 = plate["box"]
                                if px1 >= x1 and px2 <= x2 and py1 >= y1 and py2 <= y2:
                                    plate_text = plate["text"]
                                    break
                            if plate_text in violation_plates:
                                color = (255, 255, 0)
                            else:
                                color = (0, 255, 0)
                            cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), color, 2)
                            vehicle_type = {2: "Ô tô", 3: "Xe máy", 5: "Xe buýt", 7: "Xe tải"}.get(label, "Unknown")
                            cv2.putText(frame_rgb, f"{vehicle_type} - {plate_text}", 
                                      (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                return frame_rgb, violations
            except Exception as e:
                print(f"Error processing frame: {e}")
                return None, []
        return None, []

    def save_frame(self, frame, image_path):
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def is_camera_running(self):
        return self.cap is not None and self.cap.isOpened()

    def detect(self, frame):
        return self.model(frame)