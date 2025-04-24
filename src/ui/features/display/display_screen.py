# src/ui/features/display/display_screen.py
import dearpygui.dearpygui as dpg
import numpy as np
import cv2

class DisplayScreen:
    def __init__(self, view_model):
        self.view_model = view_model
        self.main_screen = None
        self.display_count = 1
        self.display_states = {}
        self.current_video = None  # Đường dẫn file video được chọn

    def create_display_panel(self, label, tag_prefix):
        self.display_states[tag_prefix] = {
            "running": False,
            "status_text_id": None,
            "video_path_id": None,  # Thay video_list_id thành video_path_id để hiển thị đường dẫn
            "result_text_id": None,
            "texture_id": None,
            "last_width": 540,
            "last_height": 350
        }

        dpg.add_spacer(height=5)

        # Tạo texture để hiển thị video
        with dpg.texture_registry():
            self.display_states[tag_prefix]["texture_id"] = dpg.add_dynamic_texture(
                width=540, height=350, default_value=np.zeros((350, 540, 4), dtype=np.float32)
            )

        # Display area
        dpg.add_child_window(tag=f"{tag_prefix}_screen", width=540, height=350, border=True)
        dpg.add_image(self.display_states[tag_prefix]["texture_id"], parent=f"{tag_prefix}_screen")

        # Status text
        status_text_id = dpg.add_text(f"[{tag_prefix}] Status: Stopped", tag=f"{tag_prefix}_status")
        self.display_states[tag_prefix]["status_text_id"] = status_text_id

        # Video path text (thay thế video_list_id)
        video_path_id = dpg.add_text(f"[{tag_prefix}] Video: None", tag=f"{tag_prefix}_video_path")
        self.display_states[tag_prefix]["video_path_id"] = video_path_id

        # Result text
        result_text_id = dpg.add_text(f"[{tag_prefix}] Result: No result yet", tag=f"{tag_prefix}_result")
        self.display_states[tag_prefix]["result_text_id"] = result_text_id

        # Các nút Load, Start, Stop, Exit
        with dpg.group(horizontal=True):
            dpg.add_button(label="Load", width=110, callback=self.load_callback, user_data=tag_prefix)
            dpg.add_button(label="Start", width=110, callback=self.start_callback, user_data=tag_prefix)
            dpg.add_button(label="Stop", width=110, callback=self.stop_callback, user_data=tag_prefix)
            dpg.add_button(label="Exit", width=110, callback=self.exit_callback, user_data=tag_prefix)

    def create(self):
        with dpg.child_window(parent="DisplayScreen", width=-1, height=-1, horizontal_scrollbar=True):
            with dpg.group(horizontal=True, tag="display_container"):
                with dpg.group():
                    self.create_display_panel("Display 1", "display1")

        dpg.add_spacer(height=10, parent="DisplayScreen")
        dpg.add_button(label="New Camera", width=130, height=50, callback=self.add_new_display, parent="DisplayScreen")

    def add_new_display(self):
        self.display_count += 1
        tag_prefix = f"display{self.display_count}"
        label = f"Display {self.display_count}"
        with dpg.group(parent="display_container"):
            self.create_display_panel(label, tag_prefix)

    def load_callback(self, sender, app_data, user_data):
        tag_prefix = user_data

        # Callback khi người dùng chọn file
        def file_dialog_callback(sender, app_data, user_data):
            tag_prefix = user_data
            # Lấy đường dẫn file từ file dialog
            file_path = app_data["file_path_name"]
            file_name = app_data["file_name"]

            # Kiểm tra định dạng file
            supported_extensions = (".mp4", ".avi")
            if not file_name.lower().endswith(supported_extensions):
                dpg.set_value(self.display_states[tag_prefix]["video_path_id"], f"[{tag_prefix}] Video: Unsupported format")
                print(f"[{tag_prefix}] Unsupported video format: {file_name}")
                return

            # Mở file video
            self.current_video = file_path
            if not self.view_model.open_video(self.current_video):
                dpg.set_value(self.display_states[tag_prefix]["video_path_id"], f"[{tag_prefix}] Video: Failed to load {file_name}")
                print(f"[{tag_prefix}] Failed to load video: {file_path}")
            else:
                dpg.set_value(self.display_states[tag_prefix]["video_path_id"], f"[{tag_prefix}] Video: {file_path}")
                print(f"[{tag_prefix}] Successfully loaded video: {file_path}")

        # Mở file dialog để chọn video
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=file_dialog_callback,
            user_data=tag_prefix,
            file_count=1,
            tag=f"{tag_prefix}_file_dialog",
            width=700,
            height=400,
            default_path="C:/",  # Đường dẫn mặc định (có thể thay đổi)
            modal=True
        ):
            # Lọc các file video (.mp4, .avi)
            dpg.add_file_extension(".mp4", color=(0, 255, 0, 255))
            dpg.add_file_extension(".avi", color=(0, 255, 0, 255))

    def start_callback(self, sender, app_data, user_data):
        tag_prefix = user_data
        if not self.display_states[tag_prefix]["running"] and self.current_video:
            self.display_states[tag_prefix]["running"] = True
            dpg.set_value(self.display_states[tag_prefix]["status_text_id"], f"[{tag_prefix}] Status: Running")
            # Bắt đầu phát video và nhận diện
            self.play_video(tag_prefix)

    def stop_callback(self, sender, app_data, user_data):
        tag_prefix = user_data
        if self.display_states[tag_prefix]["running"]:
            self.display_states[tag_prefix]["running"] = False
            dpg.set_value(self.display_states[tag_prefix]["status_text_id"], f"[{tag_prefix}] Status: Stopped")
            self.view_model.release_video()
            self.view_model.clear_result()
            dpg.set_value(self.display_states[tag_prefix]["result_text_id"], f"[{tag_prefix}] Result: No result yet")
            print(f"[{tag_prefix}] Video playback stopped")

    def exit_callback(self, sender, app_data, user_data):
        tag_prefix = user_data
        self.view_model.release_video()
        dpg.delete_item(f"{tag_prefix}_screen")
        dpg.delete_item(self.display_states[tag_prefix]["status_text_id"])
        dpg.delete_item(self.display_states[tag_prefix]["video_path_id"])
        dpg.delete_item(self.display_states[tag_prefix]["result_text_id"])
        dpg.delete_item(self.display_states[tag_prefix]["texture_id"])
        dpg.delete_item(dpg.get_item_parent(f"{tag_prefix}_screen"))
        del self.display_states[tag_prefix]
        print(f"[{tag_prefix}] Display panel removed")

    def play_video(self, tag_prefix):
        def update_frame():
            if not self.display_states[tag_prefix]["running"]:
                return

            # Lấy khung hình tiếp theo
            frame = self.view_model.get_next_frame()
            if frame is None:
                self.display_states[tag_prefix]["running"] = False
                dpg.set_value(self.display_states[tag_prefix]["status_text_id"], f"[{tag_prefix}] Status: Stopped")
                return

            # Chạy YOLOv8 để nhận diện xe cộ
            detections = self.main_screen.view_model.detect_vehicles(frame)

            # Vẽ bounding box và nhãn lên khung hình
            for detection in detections:
                x1, y1, x2, y2 = detection["bbox"]
                label = detection["label"]
                confidence = detection["confidence"]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Chuyển khung hình sang định dạng RGBA để hiển thị trong DearPyGui
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            frame_resized = cv2.resize(frame_rgb, (540, 350))
            frame_normalized = frame_resized.astype(np.float32) / 255.0

            # Cập nhật texture
            dpg.set_value(self.display_states[tag_prefix]["texture_id"], frame_normalized.flatten())

            # Cập nhật kết quả nhận diện
            if detections:
                result_text = f"Detected {len(detections)} vehicles: " + ", ".join([f"{d['label']} ({d['confidence']:.2f})" for d in detections])
            else:
                result_text = "No vehicles detected"
            dpg.set_value(self.display_states[tag_prefix]["result_text_id"], f"[{tag_prefix}] Result: {result_text}")

            # Lên lịch cập nhật khung hình tiếp theo
            dpg.set_frame_callback(1/30, update_frame)

        # Bắt đầu phát video
        update_frame()