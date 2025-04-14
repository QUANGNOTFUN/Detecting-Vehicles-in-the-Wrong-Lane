import tkinter as tk
from tkinter import ttk

class ConfigurationScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Menu điều hướng
        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(fill="x")
        tk.Button(self.menu_frame, text="Main", command=lambda: controller.show_frame("MainScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Report", command=lambda: controller.show_frame("ReportScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Config", command=lambda: controller.show_frame("ConfigurationScreen")).pack(side="left")

        # Tạo frame cho cấu hình
        self.config_frame = ttk.Frame(self)
        self.config_frame.pack(pady=20)

        # Ngưỡng phát hiện
        tk.Label(self.config_frame, text="Detection Threshold (0-1):").grid(row=0, column=0, padx=5, pady=5)
        self.threshold_entry = ttk.Entry(self.config_frame)
        self.threshold_entry.insert(0, "0.5")
        self.threshold_entry.grid(row=0, column=1, padx=5, pady=5)

        # Vùng phát hiện (giả lập)
        tk.Label(self.config_frame, text="Lane 1 X-Min:").grid(row=1, column=0, padx=5, pady=5)
        self.lane1_xmin = ttk.Entry(self.config_frame)
        self.lane1_xmin.insert(0, "0")
        self.lane1_xmin.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.config_frame, text="Lane 1 X-Max:").grid(row=2, column=0, padx=5, pady=5)
        self.lane1_xmax = ttk.Entry(self.config_frame)
        self.lane1_xmax.insert(0, "213")
        self.lane1_xmax.grid(row=2, column=1, padx=5, pady=5)

        # Nút lưu
        tk.Button(self.config_frame, text="Save", command=self.save_config).grid(row=3, column=0, columnspan=2, pady=10)

    def save_config(self):
        """Lưu cấu hình (giả lập)."""
        try:
            threshold = float(self.threshold_entry.get())
            lane1_xmin = int(self.lane1_xmin.get())
            lane1_xmax = int(self.lane1_xmax.get())
            if 0 <= threshold <= 1 and lane1_xmin < lane1_xmax:
                print(f"Saved: threshold={threshold}, lane1_xmin={lane1_xmin}, lane1_xmax={lane1_xmax}")
            else:
                print("Invalid configuration values")
        except ValueError:
            print("Invalid input format")