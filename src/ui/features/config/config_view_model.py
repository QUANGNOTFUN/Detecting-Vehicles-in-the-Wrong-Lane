import json
from typing import Optional

class ConfigViewModel:
    def __init__(self):
        self.config_value = "0"
        self.lane_vehicle_types = {}
        self.vehicle_types = [
            "car",          # Ô tô con
            "motorcycle",   # Xe máy
            "bus",         # Xe buýt
            "truck",       # Xe tải
            "bicycle"      # Xe đạp
        ]

    def update_config(self, new_value):
        if new_value == "" or new_value.isdigit():
            self.config_value = new_value if new_value else "0"
            num_lanes = int(self.config_value) if self.config_value.isdigit() else 0
            self.lane_vehicle_types = {
                f"Lane{i+1}": {vehicle: False for vehicle in self.vehicle_types}
                for i in range(num_lanes)
            }

    def update_lane_vehicle(self, lane, vehicle_type, value):
        if lane in self.lane_vehicle_types:
            self.lane_vehicle_types[lane][vehicle_type] = value

    def get_lane_vehicle_types(self):
        return self.lane_vehicle_types
    
    def save_to_json(self, file_path: str, frame_width: Optional[int] = 426) -> None:
        vehicle_class_map = {
            "car": 2, "motorcycle": 3, "bus": 5, "truck": 7, "bicycle": 1
        }
        num_lanes = int(self.config_value) if self.config_value.isdigit() else 0
        lane_width = frame_width // num_lanes if num_lanes > 0 else frame_width
        lanes = []
        for i in range(num_lanes):
            lane_name = f"Lane{i+1}"
            allowed_vehicles = [
                vehicle_class_map[vehicle]
                for vehicle, enabled in self.lane_vehicle_types.get(lane_name, {}).items()
                if enabled
            ]
            lanes.append({
                "lane_id": i + 1,
                "x_min": i * lane_width,
                "x_max": (i + 1) * lane_width,
                "allowed_vehicles": allowed_vehicles
            })
        config = {
            "detection_threshold": 0.5,
            "num_lanes": num_lanes,
            "lanes": lanes
        }
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)