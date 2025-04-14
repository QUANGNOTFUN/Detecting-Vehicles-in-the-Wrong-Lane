import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from .report_screen import ReportScreen
from .configuration_screen import ConfigurationScreen
from .main_screen import MainScreen

class MainView:
    def __init__(self, root, viewmodel):
        self.root = root
        self.viewmodel = viewmodel
        self.root.title("YOLOv8 Object Detection")
        self.root.geometry("900x600")

        # Bind ViewModel callbacks
        self.viewmodel.set_update_frame_callback(self.update_frame)
        self.viewmodel.set_error_callback(self.show_error)
        self.viewmodel.set_update_violations_callback(self.update_violations)

        # Tạo container cho các màn hình
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Tạo các màn hình
        self.frames = {}
        self.frame_classes = {
            "MainScreen": MainScreen,
            "ReportScreen": ReportScreen,
            "ConfigurationScreen": ConfigurationScreen
        }
        
        for name, F in self.frame_classes.items():
            frame = F(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainScreen")

    def show_frame(self, frame_name):
        """Hiển thị màn hình được chọn."""
        frame = self.frames[frame_name]
        frame.tkraise()

    def create_widgets(self):
        # Di chuyển vào MainScreen
        pass

    def update_frame(self, frame):
        """Cập nhật frame lên giao diện."""
        if self.frames["MainScreen"].winfo_viewable():
            self.frames["MainScreen"].update_frame(frame)

    def show_error(self, message):
        """Hiển thị thông báo lỗi."""
        messagebox.showerror("Error", message)

    def update_violations(self, violation):
        """Cập nhật danh sách vi phạm."""
        if self.frames["MainScreen"].winfo_viewable():
            self.frames["MainScreen"].update_violations(violation)

    def update_button_states(self, is_running):
        """Cập nhật trạng thái nút (không dùng trực tiếp ở đây)."""
        pass

    def close(self):
        """Đóng ứng dụng."""
        self.viewmodel.exit_app()
        self.root.quit()