import threading
import csv
import os

def save_violation(violation):
    file_exists = os.path.isfile('violations.csv')
    with open('violations.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Vehicle Type', 'Lane ID', 'Image Path', 'License Plate'])
        writer.writerow([
            violation['timestamp'],
            violation['vehicle_type'],
            violation['lane_id'],
            violation['image_path'],
            violation['license_plate']
        ])

class YoloViewModel:
    def __init__(self, model):
        self.model = model
        self.running = False
        self.update_frame_callback = None
        self.error_callback = None
        self.update_violations_callback = None

    def set_update_frame_callback(self, callback):
        self.update_frame_callback = callback

    def set_error_callback(self, callback):
        self.error_callback = callback

    def set_update_violations_callback(self, callback):
        self.update_violations_callback = callback

    def start_camera(self):
        if not self.running:
            try:
                self.model.start_camera()
                self.running = True
                threading.Thread(target=self.process_frames, daemon=True).start()
            except Exception as e:
                if self.error_callback:
                    self.error_callback(str(e))

    def start_video(self, video_path):
        if not self.running:
            try:
                self.model.start_camera(video_path=video_path)
                self.running = True
                threading.Thread(target=self.process_frames, daemon=True).start()
            except Exception as e:
                if self.error_callback:
                    self.error_callback(str(e))

    def stop_camera(self):
        if self.running:
            self.running = False
            self.model.stop_camera()
            if self.update_frame_callback:
                self.update_frame_callback(None)

    def process_frames(self):
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
        self.stop_camera()

    def exit_app(self):
        if self.running:
            self.stop_camera()
        self.model.stop_camera()

    def update_lane_config(self, config_data):
        self.model.update_lane_config(config_data)