import cv2
from ultralytics import YOLO

class YoloModel:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.cap = None

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

    def get_frame(self):
        """Lấy và xử lý frame từ camera với YOLO."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                results = self.model.predict(source=frame, save=False)
                annotated_frame = results[0].plot()
                return cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        return None

    def is_camera_running(self):
        """Kiểm tra trạng thái camera."""
        return self.cap is not None and self.cap.isOpened()
    