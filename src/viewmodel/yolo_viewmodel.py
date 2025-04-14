import threading
import csv
import os

def save_violation(violation):
    """Lưu vi phạm vào file CSV."""
    file_exists = os.path.isfile('violations.csv')
    with open('violations.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Vehicle Type', 'Lane ID', 'Image Path'])
        writer.writerow([
            violation['timestamp'],
            violation['vehicle_type'],
            violation['lane_id'],
            violation['image_path']
        ])

class YoloViewModel:
    def __init__(self, model):
        self.model = model
        self.running = False
        self.update_frame_callback = None
        self.error_callback = None
        self.update_violations_callback = None

    def set_update_frame_callback(self, callback):
        """Đặt callback để cập nhật frame."""
        self.update_frame_callback = callback

    def set_error_callback(self, callback):
        """Đặt callback để hiển thị lỗi."""
        self.error_callback = callback

    def set_update_violations_callback(self, callback):
        """Đặt callback để cập nhật danh sách vi phạm."""
        self.update_violations_callback = callback

    def start_camera(self):
        """Bắt đầu camera và xử lý frame."""
        if not self.running:
            try:
                self.model.start_camera()
                self.running = True
                threading.Thread(target=self.process_frames, daemon=True).start()
            except Exception as e:
                if self.error_callback:
                    self.error_callback(str(e))

    def stop_camera(self):
        """Dừng camera."""
        if self.running:
            self.running = False
            self.model.stop_camera()
            if self.update_frame_callback:
                self.update_frame_callback(None)

    def process_frames(self):
        """Xử lý và gửi frame đến View."""
        while self.running and self.model.is_camera_running():
            frame, violations = self.model.get_frame()
            if frame is None:
                break
            for violation in violations:
                save_violation(violation)
                self.model.save_frame(frame, violation['image_path'])
                if self.update_violations_callback:
                    self.update_violations_callback(violation)
            if self.update_frame_callback:
                self.update_frame_callback(frame)
        if self.running:
            self.stop_camera()

    def exit_app(self):
        """Thoát ứng dụng."""
        if self.running:
            self.stop_camera()
        self.model.stop_camera()