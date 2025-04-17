# lane_display_screen.py
import tkinter as tk
from tkinter import ttk
import numpy as np

class LaneDisplayScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Menu điều hướng
        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(fill="x")
        tk.Button(self.menu_frame, text="Main", command=lambda: controller.show_frame("MainScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Report", command=lambda: controller.show_frame("ReportScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Config", command=lambda: controller.show_frame("ConfigurationScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Lane Display", command=lambda: controller.show_frame("LaneDisplayScreen")).pack(side="left")

        # Canvas để vẽ làn đường
        self.canvas = tk.Canvas(self, bg="black", width=800, height=400)
        self.canvas.pack(fill="both", expand=True, pady=10)

        # Thông tin vi phạm
        self.info_label = tk.Label(self, text="No violations detected", font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.lane_config = None
        self.lane_objects = []  # Lưu trữ các đối tượng hình chữ nhật của làn đường
        self.vehicle_objects = []  # Lưu trữ các đối tượng phương tiện

    def update_lane_config(self, config_data):
        """Cập nhật cấu hình làn đường và vẽ sơ đồ."""
        self.lane_config = config_data["lanes"]
        self.canvas.delete("lane")  # Xóa các làn đường cũ
        self.lane_objects.clear()

        canvas_width = 800
        frame_width = 640  # Giả định chiều rộng khung hình
        scale = canvas_width / frame_width  # Tỷ lệ để vẽ lên canvas

        for lane in self.lane_config:
            x_min = lane["x_min"] * scale
            x_max = lane["x_max"] * scale
            lane_id = lane["lane_id"]
            # Vẽ hình chữ nhật đại diện cho làn đường
            rect = self.canvas.create_rectangle(
                x_min, 50, x_max, 350, outline="white", fill="gray", tags="lane"
            )
            self.canvas.create_text(
                (x_min + x_max) / 2, 30, text=f"Lane {lane_id}", fill="white", tags="lane"
            )
            self.lane_objects.append(rect)

    def update_frame(self, frame, violations, lane_lines):
        """Cập nhật sơ đồ với vị trí phương tiện và vi phạm."""
        self.canvas.delete("vehicle")  # Xóa các phương tiện cũ
        self.vehicle_objects.clear()

        if not self.lane_config:
            return

        canvas_width = 800
        frame_width = 640
        scale = canvas_width / frame_width

        # Vẽ vạch kẻ đường (nếu có)
        self.canvas.delete("line")
        if lane_lines:
            for x1, y1, x2, y2 in lane_lines:
                self.canvas.create_line(
                    x1 * scale, 50, x2 * scale, 350, fill="yellow", tags="line"
                )

        # Vẽ phương tiện và vi phạm
        for violation in violations:
            x_center = violation.get("x_center", 0) * scale
            lane_id = violation["lane_id"]
            vehicle_type = violation["vehicle_type"]
            license_plate = violation["license_plate"]

            vehicle = self.canvas.create_rectangle(
                x_center - 20, 150, x_center + 20, 250,
                fill="red", outline="white", tags="vehicle"
            )
            # Thêm nhãn thông tin
            self.canvas.create_text(
                x_center, 130, text=f"{vehicle_type}\n{license_plate}",
                fill="white", tags="vehicle"
            )
            self.vehicle_objects.append(vehicle)

            # Tìm làn đường tương ứng
            for lane in self.lane_config:
                if lane["lane_id"] == lane_id:
                    x_min = lane["x_min"] * scale
                    x_max = lane["x_max"] * scale
                    # Vẽ phương tiện (hình chữ nhật đỏ cho vi phạm)
                    vehicle = self.canvas.create_rectangle(
                        x_center - 20, 150, x_center + 20, 250,
                        fill="red", outline="white", tags="vehicle"
                    )
                    self.vehicle_objects.append(vehicle)
                    # Cập nhật thông tin vi phạm
                    self.info_label.config(
                        text=f"Violation: {vehicle_type}, Lane {lane_id}, Plate: {license_plate}"
                    )
                    break