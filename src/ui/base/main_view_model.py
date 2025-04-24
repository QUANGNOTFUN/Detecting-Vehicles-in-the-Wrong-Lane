# src/ui/base/main_view_model.py
from ultralytics import YOLO
import cv2
import numpy as np

class MainViewModel:
    def __init__(self):
        self.message = "Hello from MainViewModel!"
        self.model = None
        self.detection_results = []  # Lưu kết quả nhận diện

        # Load mô hình YOLOv8
        self.load_yolo_model()

    def load_yolo_model(self):
        try:
            # Load mô hình YOLOv8 (dùng mô hình pre-trained như yolov8n.pt)
            self.model = YOLO("yolov8n.pt")  # Có thể thay bằng yolov8s.pt, yolov8m.pt, v.v.
            self.message = "YOLOv8 model loaded successfully!"
        except Exception as e:
            self.message = f"Failed to load YOLOv8 model: {str(e)}"
            self.model = None

    def detect_vehicles(self, frame):
        if self.model is None:
            return []

        try:
            # Chuyển khung hình sang định dạng phù hợp cho YOLOv8
            results = self.model(frame)
            
            # Lấy kết quả nhận diện
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Lấy tọa độ và nhãn
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    label = result.names[int(box.cls)]
                    confidence = box.conf.cpu().numpy()
                    
                    # Chỉ giữ các đối tượng là xe cộ (car, truck, bus, v.v.)
                    if label in ["car", "truck", "bus", "motorbike"]:
                        detections.append({
                            "label": label,
                            "confidence": float(confidence),
                            "bbox": (int(x1), int(y1), int(x2), int(y2))
                        })
            
            self.detection_results = detections
            return detections
        except Exception as e:
            self.message = f"Detection failed: {str(e)}"
            return []

    def update_message(self, new_message):
        self.message = new_message

    def get_detection_results(self):
        return self.detection_results