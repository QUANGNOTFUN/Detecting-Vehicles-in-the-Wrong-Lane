import dearpygui.dearpygui as dpg
import cv2
import numpy as np
from src.ui.features.display.display_view_model import DisplayViewModel
from src.model.yolo_model import YoloModel
import tkinter as tk
from tkinter import filedialog
import threading

class DisplayScreen:
    def __init__(self, view_model: DisplayViewModel, config_view_model):
        self.view_model = view_model
        self.config_view_model = config_view_model
        self.main_screen = None
        self.display_count = 1
        self.active_cameras = {}
        self.textures = {}
        self.is_running = {}
        self.yolo_models = {}
        self.texture_registry = dpg.add_texture_registry(label="TextureRegistry")
        self.model_path = "yolov8m.pt"  # Cập nhật đường dẫn đến mô hình YOLO

    def create_display_panel(self, label, tag_prefix):
        with dpg.group(tag=tag_prefix, horizontal=False):
            with dpg.group(horizontal=True):
                dpg.add_button(label=label, width=100, callback=lambda: self.update_ui(tag_prefix))
                dpg.add_button(label="Report chart", width=110, callback=lambda: self.main_screen.show_frame("ChartScreen"))
                dpg.add_button(label="Config Lane", width=110, callback=lambda: self.main_screen.show_frame("ConfigScreen"))

            dpg.add_spacer(height=5)

            dpg.add_child_window(tag=f"{tag_prefix}_screen", width=640, height=350, border=True)
            
            self.textures[tag_prefix] = dpg.add_raw_texture(
                width=540,
                height=350,
                default_value=np.zeros((350, 540, 4), dtype=np.float32),
                format=dpg.mvFormat_Float_rgba,
                parent=self.texture_registry
            )

            with dpg.drawlist(width=540, height=350, parent=f"{tag_prefix}_screen", tag=f"{tag_prefix}_drawlist"):
                dpg.draw_rectangle((0, 0), (540, 350), color=(0, 0, 0, 255), fill=(0, 0, 0, 255))
                dpg.draw_image(self.textures[tag_prefix], (0, 0), (540, 350), tag=f"{tag_prefix}_image")

            with dpg.group(horizontal=True):
                dpg.add_button(label="Start camera", width=110, callback=lambda: self.start_camera(tag_prefix))
                dpg.add_button(label="Load", width=110, callback=lambda: self.load_file(tag_prefix))
                dpg.add_button(label="Stop", width=110, callback=lambda: self.stop_camera(tag_prefix))
                dpg.add_button(label="Exit", width=110, callback=lambda: self.exit_display(tag_prefix))

        self.active_cameras[tag_prefix] = None
        self.is_running[tag_prefix] = False
        # Truyền ConfigViewModel vào YoloModel thay vì config_path
        self.yolo_models[tag_prefix] = YoloModel(self.model_path, self.config_view_model)

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

    def start_camera(self, tag_prefix):
        if self.active_cameras.get(tag_prefix) is None:
            yolo_model = self.yolo_models.get(tag_prefix)
            try:
                yolo_model.start_camera()
                print(f"[{tag_prefix}] Đã mở camera thành công.")
                self.active_cameras[tag_prefix] = yolo_model
                self.is_running[tag_prefix] = True
                threading.Thread(target=self.update_camera_frame, args=(tag_prefix,), daemon=True).start()
            except Exception as e:
                print(f"[{tag_prefix}] Không thể mở camera: {e}")

    def update_camera_frame(self, tag_prefix):
        while self.is_running.get(tag_prefix, False):
            yolo_model = self.active_cameras.get(tag_prefix)
            if yolo_model is None:
                break

            frame, violations = yolo_model.get_frame()
            if frame is not None:
                frame = cv2.resize(frame, (540, 350))
                frame_rgba = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
                dpg.set_value(self.textures[tag_prefix], frame_rgba.astype(np.float32) / 255.0)

            cv2.waitKey(1)

    def load_file(self, tag_prefix):
        self.stop_camera(tag_prefix)

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("Video files", "*.mp4 *.avi"),
                ("Image files", "*.jpg *.png"),
                ("All files", "*.*")
            ],
            initialdir="::{20D04FE0-3AEA-1069-A2D8-08002B30309D}"
        )
        root.destroy()

        if file_path:
            self.load_file_callback(file_path, tag_prefix)

    def load_file_callback(self, file_path, tag_prefix):
        yolo_model = self.yolo_models.get(tag_prefix)
        if file_path.endswith((".mp4", ".avi")):
            try:
                yolo_model.start_camera(file_path)
                self.active_cameras[tag_prefix] = yolo_model
                self.is_running[tag_prefix] = True
                threading.Thread(target=self.update_camera_frame, args=(tag_prefix,), daemon=True).start()
            except Exception as e:
                print(f"[{tag_prefix}] Không thể mở file video: {file_path}, {e}")
        elif file_path.endswith((".jpg", ".png")):
            image = cv2.imread(file_path)
            if image is None:
                print(f"[{tag_prefix}] Không thể mở file hình ảnh: {file_path}")
                return
            results = yolo_model.detect(image)
            license_plates = yolo_model.detect_license_plates(image, results)
            violations = yolo_model.check_violation(results, license_plates, image)
            violation_plates = {v["license_plate"] for v in violations}
            for result in results:
                boxes = result.boxes.xyxy.cpu().numpy()
                labels = result.boxes.cls.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                for box, label, conf in zip(boxes, labels, confidences):
                    if conf < yolo_model.detection_threshold or label not in [2, 3, 5, 7]:
                        continue
                    x1, y1, x2, y2 = box.astype(int)
                    plate_text = "Unknown"
                    for plate in license_plates:
                        px1, py1, px2, py2 = plate["box"]
                        if px1 >= x1 and px2 <= x2 and py1 >= y1 and py2 <= y2:
                            plate_text = plate["text"]
                            break
                    color = (255, 0, 0) if plate_text in violation_plates else (0, 255, 0)
                    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                    vehicle_type = {2: "Ô tô", 3: "Xe máy", 5: "Xe buýt", 7: "Xe tải"}.get(label, "Unknown")
                    cv2.putText(image, f"{vehicle_type} - {plate_text}", 
                                (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            image = cv2.resize(image, (540, 350))
            image_rgba = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            dpg.set_value(self.textures[tag_prefix], image_rgba.astype(np.float32) / 255.0)

    def stop_camera(self, tag_prefix):
        if self.active_cameras.get(tag_prefix) is not None:
            self.active_cameras[tag_prefix].stop_camera()
            self.active_cameras[tag_prefix] = None
        self.is_running[tag_prefix] = False
        black_screen = np.zeros((350, 540, 4), dtype=np.float32)
        dpg.set_value(self.textures[tag_prefix], black_screen)

    def exit_display(self, tag_prefix):
        self.stop_camera(tag_prefix)
        dpg.delete_item(self.textures[tag_prefix])
        del self.textures[tag_prefix]
        del self.active_cameras[tag_prefix]
        del self.is_running[tag_prefix]
        del self.yolo_models[tag_prefix]
        dpg.delete_item(tag_prefix)

    def update_ui(self, tag_prefix):
        self.view_model.update_data()
        print(f"[{tag_prefix}] Data updated: {self.view_model.display_data}")