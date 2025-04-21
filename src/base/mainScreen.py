import dearpygui.dearpygui as dpg
from PIL import Image
import numpy as np
import cv2

class MainScreen:
    def __init__(self, viewmodel):
        self.viewmodel = viewmodel
        # Đăng ký các callback
        self.viewmodel.set_update_frame_callback(self.update_frame)
        self.viewmodel.set_update_violations_callback(self.update_violations)
        self.setup_gui()

    def setup_gui(self):
        # Initialize DearPyGui
        dpg.create_context()
        dpg.create_viewport(
            title="Vehicle Detection System",
            width=1280,
            height=720,
            resizable=True
        )

        dpg.setup_dearpygui()

        # Main Window
        with dpg.window(label="Main Window", tag="main_window"):
            # Menu Bar
            with dpg.menu_bar():
                dpg.add_button(label="Main", callback=lambda: self.show_frame("MainScreen"))
                dpg.add_button(label="Report", callback=lambda: self.show_frame("ReportScreen"))
                dpg.add_button(label="Config", callback=lambda: self.show_frame("ConfigurationScreen"))

            # Video Display
            with dpg.group(horizontal=False):
                dpg.add_text("No camera or video running", tag="video_status")
                with dpg.texture_registry():
                    dpg.add_raw_texture(width=640, height=480, default_value=np.zeros((480, 640, 3), dtype=np.float32), 
                                      format=dpg.mvFormat_Float_rgb, tag="video_texture")
                dpg.add_image("video_texture", width=640, height=480)

            # Violations Table
            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                          borders_innerH=True, borders_outerH=True, borders_innerV=True,
                          borders_outerV=True, tag="violations_table"):
                dpg.add_table_column(label="Timestamp")
                dpg.add_table_column(label="Vehicle Type")
                dpg.add_table_column(label="Lane ID")
                dpg.add_table_column(label="License Plate")

            # Control Buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Camera", callback=self.viewmodel.start_camera, tag="start_button")
                dpg.add_button(label="Load Video", callback=self.load_video, tag="video_button")
                dpg.add_button(label="Stop", callback=self.stop_action, tag="stop_button", enabled=False)
                dpg.add_button(label="Exit", callback=self.exit_app)

        dpg.show_viewport()

    def show_frame(self, frame_name):
        print(f"Switching to {frame_name}")  # Tạm thời chỉ in ra console

    def load_video(self):
        # Open file dialog
        with dpg.file_dialog(label="Choose Video File", callback=self._video_dialog_callback,
                            file_count=1, modal=True):
            dpg.add_file_extension(".mp4", color=(0, 255, 0, 255))
            dpg.add_file_extension(".avi", color=(0, 255, 0, 255))
            dpg.add_file_extension(".mov", color=(0, 255, 0, 255))
            dpg.add_file_extension(".*")

    def _video_dialog_callback(self, sender, app_data):
        if app_data['file_path_name']:
            self.viewmodel.start_video(app_data['file_path_name'])
            self.update_button_states(running=True)

    def stop_action(self):
        self.viewmodel.stop_camera()
        self.update_button_states(running=False)

    def exit_app(self):
        self.viewmodel.exit_app()
        dpg.destroy_context()

    def update_button_states(self, running):
        dpg.configure_item("start_button", enabled=not running)
        dpg.configure_item("video_button", enabled=not running)
        dpg.configure_item("stop_button", enabled=running)
        if not running:
            dpg.set_value("video_status", "No camera or video running")

    def update_frame(self, frame):
        if frame is not None:
            # Convert frame to float32 and normalize to 0-1 range
            frame = frame.astype(np.float32) / 255.0
            # Resize frame if needed
            frame = cv2.resize(frame, (640, 480))
            dpg.set_value("video_texture", frame.ravel())
            dpg.set_value("video_status", "")
            self.update_button_states(running=True)
        else:
            dpg.set_value("video_status", "No camera or video running")
            self.update_button_states(running=False)

    def update_violations(self, violation):
        with dpg.table_row(parent="violations_table"):
            dpg.add_text(violation['timestamp'])
            dpg.add_text(violation['vehicle_type'])
            dpg.add_text(violation['lane_id'])
            dpg.add_text(violation['license_plate'])

    def run(self):
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
        dpg.destroy_context()