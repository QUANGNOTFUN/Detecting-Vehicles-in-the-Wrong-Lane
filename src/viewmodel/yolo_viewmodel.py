import threading

class YoloViewModel:
    def __init__(self, model):
        self.model = model
        self.running = False
        self.update_frame_callback = None
        self.error_callback = None

    def set_update_frame_callback(self, callback):
        """Đặt callback để cập nhật frame."""
        self.update_frame_callback = callback

    def set_error_callback(self, callback):
        """Đặt callback để hiển thị lỗi."""
        self.error_callback = callback

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
            frame = self.model.get_frame()
            if frame is None:
                break
            if self.update_frame_callback:
                self.update_frame_callback(frame)
        if self.running:
            self.stop_camera()

    def exit_app(self):
        """Thoát ứng dụng."""
        if self.running:
            self.stop_camera()
        self.model.stop_camera()