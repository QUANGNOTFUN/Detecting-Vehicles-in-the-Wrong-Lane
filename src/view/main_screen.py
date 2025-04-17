import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from .configuration_screen import ConfigurationScreen

class MainScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(fill="x")
        tk.Button(self.menu_frame, text="Main", command=lambda: controller.show_frame("MainScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Report", command=lambda: controller.show_frame("ReportScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Config", command=lambda: controller.show_frame("ConfigurationScreen")).pack(side="left")

        self.video_label = tk.Label(self, text="No camera or video running", font=("Arial", 12))
        self.video_label.pack(pady=10)

        self.violations_frame = tk.Frame(self)
        self.violations_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(self.violations_frame, columns=('Timestamp', 'Vehicle', 'Lane', 'License Plate'), show='headings')
        self.tree.heading('Timestamp', text='Timestamp')
        self.tree.heading('Vehicle', text='Vehicle Type')
        self.tree.heading('Lane', text='Lane ID')
        self.tree.heading('License Plate', text='License Plate')
        self.tree.pack(fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.violations_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)
        self.start_button = tk.Button(self.button_frame, text="Start Camera", command=self.controller.viewmodel.start_camera, width=15)
        self.start_button.grid(row=0, column=0, padx=5)
        self.video_button = tk.Button(self.button_frame, text="Load Video", command=self.load_video, width=15)
        self.video_button.grid(row=0, column=1, padx=5)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_action, width=15, state="disabled")
        self.stop_button.grid(row=0, column=2, padx=5)
        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.controller.close, width=15)
        self.exit_button.grid(row=0, column=3, padx=5)
    
    def update_button_states(self, running):
        states = self.controller.viewmodel.update_button_states(running)
        self.start_button.configure(state=states["start_button"])
        self.video_button.configure(state=states["video_button"])
        self.stop_button.configure(state=states["stop_button"])

    def load_video(self):
        video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        if video_path:
            self.controller.viewmodel.start_video(video_path)
            self.update_button_states(running=True)

    def stop_action(self):
        self.controller.viewmodel.stop_camera()
        self.update_button_states(running=False)

    def update_button_states(self, running):
        if running:
            self.start_button.configure(state="disabled")
            self.video_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
        else:
            self.start_button.configure(state="normal")
            self.video_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.video_label.configure(image="", text="No camera or video running")

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

    def update_violations(self, violation):
        self.tree.insert('', 'end', values=(
            violation['timestamp'],
            violation['vehicle_type'],
            violation['lane_id'],
            violation['license_plate']
        ))