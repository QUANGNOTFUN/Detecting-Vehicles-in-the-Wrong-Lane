import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class MainView:
    def __init__(self, root, viewmodel):
        self.root = root
        self.viewmodel = viewmodel
        self.root.title("YOLOv8 Object Detection")
        self.root.geometry("900x600")

        # Bind ViewModel commands
        self.viewmodel.set_update_frame_callback(self.update_frame)
        self.viewmodel.set_error_callback(self.show_error)

        self.create_widgets()

    def create_widgets(self):
        # Video label
        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=10)

        # Button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)

        # Buttons
        self.start_button = tk.Button(
            self.button_frame, text="Start Camera", command=self.viewmodel.start_camera, width=15
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(
            self.button_frame, text="Stop Camera", command=self.viewmodel.stop_camera, width=15
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        self.stop_button.config(state="disabled")

        self.exit_button = tk.Button(
            self.button_frame, text="Exit", command=self.viewmodel.exit_app, width=15
        )
        self.exit_button.grid(row=0, column=2, padx=5)

    def update_frame(self, frame):
        """Cập nhật frame lên giao diện."""
        if frame is not None:
            img = Image.fromarray(frame)
            img = img.resize((640, 480), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        else:
            self.video_label.configure(image="")

    def show_error(self, message):
        """Hiển thị thông báo lỗi."""
        messagebox.showerror("Error", message)

    def update_button_states(self, is_running):
        """Cập nhật trạng thái nút."""
        self.start_button.config(state="normal" if is_running else "disabled")
        self.stop_button.config(state="disabled" if is_running else "normal")

    def close(self):
        """Đóng ứng dụng."""
        self.root.quit()