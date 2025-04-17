import tkinter as tk
from tkinter import ttk
import json

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

        # Số lượng làn đường
        tk.Label(self.config_frame, text="Number of Lanes (1-5):").grid(row=1, column=0, padx=5, pady=5)
        self.num_lanes_entry = ttk.Entry(self.config_frame)
        self.num_lanes_entry.insert(0, "3")
        self.num_lanes_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.config_frame, text="Update Lanes", command=self.update_lane_config).grid(row=1, column=2, padx=5, pady=5)

        # Frame cho cấu hình làn đường
        self.lanes_frame = ttk.Frame(self.config_frame)
        self.lanes_frame.grid(row=2, column=0, columnspan=3, pady=10)
        self.lane_configs = []
        self.vehicle_types = {
            "Ô tô": 2,  # Nhãn YOLO cho ô tô
            "Xe máy": 3,  # Nhãn YOLO cho xe máy
            "Xe buýt": 5,  # Nhãn YOLO cho xe buýt
            "Xe tải": 7   # Nhãn YOLO cho xe tải
        }

        # Nút lưu
        tk.Button(self.config_frame, text="Save", command=self.save_config).grid(row=3, column=0, columnspan=3, pady=10)

    def update_lane_config(self):
        """Cập nhật giao diện cấu hình làn đường dựa trên số lượng làn."""
        try:
            num_lanes = int(self.num_lanes_entry.get())
            if not 1 <= num_lanes <= 5:
                raise ValueError("Number of lanes must be between 1 and 5")

            # Xóa các widget cũ
            for widget in self.lanes_frame.winfo_children():
                widget.destroy()
            self.lane_configs.clear()

            # Tạo giao diện cho từng làn
            for lane_id in range(1, num_lanes + 1):
                lane_frame = ttk.LabelFrame(self.lanes_frame, text=f"Lane {lane_id}")
                lane_frame.pack(fill="x", padx=5, pady=5)
                tk.Label(lane_frame, text=f"Lane {lane_id} X-Min:").grid(row=0, column=0, padx=5, pady=5)
                xmin_entry = ttk.Entry(lane_frame, width=10)
                xmin_entry.insert(0, str((lane_id - 1) * 213))  # Giả định mặc định
                xmin_entry.grid(row=0, column=1, padx=5, pady=5)
                tk.Label(lane_frame, text=f"Lane {lane_id} X-Max:").grid(row=1, column=0, padx=5, pady=5)
                xmax_entry = ttk.Entry(lane_frame, width=10)
                xmax_entry.insert(0, str(lane_id * 213))
                xmax_entry.grid(row=1, column=1, padx=5, pady=5)

                # Checkbutton cho loại xe
                tk.Label(lane_frame, text="Allowed Vehicles:").grid(row=2, column=0, padx=5, pady=5)
                vehicle_vars = {}
                col = 1
                for vehicle, label_id in self.vehicle_types.items():
                    var = tk.BooleanVar(value=True)  # Mặc định cho phép tất cả
                    tk.Checkbutton(lane_frame, text=vehicle, variable=var).grid(row=2, column=col, sticky="w", padx=5)
                    vehicle_vars[vehicle] = var
                    col += 1

                self.lane_configs.append({
                    "lane_id": lane_id,
                    "xmin_entry": xmin_entry,
                    "xmax_entry": xmax_entry,
                    "vehicle_vars": vehicle_vars
                })

        except ValueError as e:
            print(f"Error: {e}")

    # configuration_screen.py
    def save_config(self):
        try:
            threshold = float(self.threshold_entry.get())
            num_lanes = int(self.num_lanes_entry.get())
            if not 0 <= threshold <= 1:
                raise ValueError("Threshold must be between 0 and 1")
            if not 1 <= num_lanes <= 5:
                raise ValueError("Number of lanes must be between 1 and 5")

            lane_configurations = []
            for config in self.lane_configs:
                lane_id = config["lane_id"]
                xmin = int(config["xmin_entry"].get())
                xmax = int(config["xmax_entry"].get())
                if xmin >= xmax:
                    raise ValueError(f"X-Min must be less than X-Max for Lane {lane_id}")

                allowed_vehicles = [
                    self.vehicle_types[vehicle]
                    for vehicle, var in config["vehicle_vars"].items()
                    if var.get()
                ]
                lane_configurations.append({
                    "lane_id": lane_id,
                    "x_min": xmin,
                    "x_max": xmax,
                    "allowed_vehicles": allowed_vehicles
                })

            config_data = {
                "detection_threshold": threshold,
                "num_lanes": num_lanes,
                "lanes": lane_configurations
            }
            print("Saved configuration:", json.dumps(config_data, indent=2))

            with open("lane_config.json", "w") as f:
                json.dump(config_data, f, indent=2)

            # Truyền cấu hình đến YoloModel và LaneDisplayScreen
            self.controller.viewmodel.update_lane_config(config_data)
            if "LaneDisplayScreen" in self.controller.frames:
                self.controller.frames["LaneDisplayScreen"].update_lane_config(config_data)

        except ValueError as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            print(f"Error saving config: {e}")