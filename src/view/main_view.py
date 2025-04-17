import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

from .lane_display_screen import LaneDisplayScreen
from .report_screen import ReportScreen
from .configuration_screen import ConfigurationScreen
from .main_screen import MainScreen

class MainView:
    def __init__(self, root, viewmodel):
        self.root = root
        self.viewmodel = viewmodel
        self.root.title("YOLOv8 Object Detection")
        self.root.geometry("900x600")

        self.viewmodel.set_update_frame_callback(self.update_frame)
        self.viewmodel.set_error_callback(self.show_error)
        self.viewmodel.set_update_violations_callback(self.update_violations)

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self.frame_classes = {
            "MainScreen": MainScreen,
            "ReportScreen": ReportScreen,
            "ConfigurationScreen": ConfigurationScreen,
            "LaneDisplayScreen": LaneDisplayScreen  # Thêm màn hình mới
        }

        for name, F in self.frame_classes.items():
            frame = F(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainScreen")

    def update_frame(self, frame):
        if frame is not None:
            img = Image.fromarray(frame)
            img = img.resize((640, 480), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk, text="")
            self.update_button_states(running=True)
        else:
            self.video_label.configure(image="", text="No camera or video running")
            self.update_button_states(running=False)

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def create_widgets(self):
        pass

    def update_frame(self, frame):
        """Cập nhật frame cho MainScreen."""
        if self.frames["MainScreen"].winfo_viewable():
            self.frames["MainScreen"].update_frame(frame)

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def update_violations(self, violation):
        if self.frames["MainScreen"].winfo_viewable():
            self.frames["MainScreen"].update_violations(violation)

    def close(self):
        self.viewmodel.exit_app()
        self.root.quit()