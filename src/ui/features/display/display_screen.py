import dearpygui.dearpygui as dpg
import cv2
import numpy as np
from src.ui.features.display.display_view_model import DisplayViewModel
import tkinter as tk
from tkinter import filedialog
import threading

class DisplayScreen:
    def __init__(self, view_model: DisplayViewModel):
        self.view_model = view_model
        self.main_screen = None
        self.display_count = 1
        self.active_cameras = {}
        self.textures = {}
        self.is_running = {}
        self.texture_registry = dpg.add_texture_registry(label="TextureRegistry")

    def create_display_panel(self, label, tag_prefix):
        with dpg.group(tag=tag_prefix, horizontal=False):
            with dpg.group(horizontal=True):
                dpg.add_button(label=label, width=100, callback=lambda: self.update_ui(tag_prefix))
                dpg.add_button(label="Report chart", width=110)
                dpg.add_button(label="Config Lane", width=110)

            dpg.add_spacer(height=5)

            dpg.add_child_window(tag=f"{tag_prefix}_screen", width=540, height=350, border=True)
            
            # Khởi tạo texture và image ngay từ đầu
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
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                print(f"[{tag_prefix}] Không thể mở camera!")
                return
            print(f"[{tag_prefix}] Đã mở camera thành công.")
            self.active_cameras[tag_prefix] = camera
            self.is_running[tag_prefix] = True
            threading.Thread(target=self.update_camera_frame, args=(tag_prefix,), daemon=True).start()

    def update_camera_frame(self, tag_prefix):
        while self.is_running.get(tag_prefix, False):
            camera = self.active_cameras.get(tag_prefix)
            if camera is None:
                break

            ret, frame = camera.read()
            if ret:
                frame = cv2.resize(frame, (540, 350))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                dpg.set_value(self.textures[tag_prefix], frame_rgb.astype(np.float32) / 255.0)

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
        if file_path.endswith((".mp4", ".avi")):
            camera = cv2.VideoCapture(file_path)
            if not camera.isOpened():
                print(f"[{tag_prefix}] Không thể mở file video: {file_path}")
                return
            self.active_cameras[tag_prefix] = camera
            self.is_running[tag_prefix] = True
            threading.Thread(target=self.update_camera_frame, args=(tag_prefix,), daemon=True).start()
        elif file_path.endswith((".jpg", ".png")):
            image = cv2.imread(file_path)
            if image is None:
                print(f"[{tag_prefix}] Không thể mở file hình ảnh: {file_path}")
                return
            image = cv2.resize(image, (540, 350))
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
            dpg.set_value(self.textures[tag_prefix], image_rgb.astype(np.float32) / 255.0)

    def stop_camera(self, tag_prefix):
        if self.active_cameras.get(tag_prefix) is not None:
            self.active_cameras[tag_prefix].release()
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
        dpg.delete_item(tag_prefix)

    def update_ui(self, tag_prefix):
        self.view_model.update_data()
        print(f"[{tag_prefix}] Data updated: {self.view_model.display_data}")
