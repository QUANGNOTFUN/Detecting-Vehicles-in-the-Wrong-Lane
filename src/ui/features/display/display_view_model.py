# src/ui/features/display/display_view_model.py
import os
import cv2

class DisplayViewModel:
    def __init__(self):
        self.display_data = "Initial Data"
        self.video_file = None  # Đường dẫn file video được chọn
        self.violation_result = "No result yet"
        self.video_cap = None  # OpenCV VideoCapture
        self.current_frame = None  # Khung hình hiện tại

    def open_video(self, video_path):
        self.video_file = video_path
        self.video_cap = cv2.VideoCapture(video_path)
        if not self.video_cap.isOpened():
            self.violation_result = f"Error: Cannot open video {video_path}"
            return False
        return True

    def get_next_frame(self):
        if self.video_cap is None or not self.video_cap.isOpened():
            return None
        ret, frame = self.video_cap.read()
        if not ret:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Quay lại đầu video nếu hết
            ret, frame = self.video_cap.read()
        if ret:
            self.current_frame = frame
            return frame
        return None

    def release_video(self):
        if self.video_cap is not None:
            self.video_cap.release()
            self.video_cap = None

    def process_violation_detection(self):
        # Phương thức này không cần sửa vì không còn dùng danh sách video
        self.violation_result = f"Processing {self.video_file} for violation detection"
        return self.violation_result

    def clear_result(self):
        self.violation_result = "No result yet"