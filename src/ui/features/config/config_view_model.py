class ConfigViewModel:
    def __init__(self):
        # Thiết lập mặc định: 2 làn
        self.config_value = "2"
        self.vehicle_types = ["car", "motorcycle", "bus", "truck"]
        self.detection_threshold = 0.5  # Ngưỡng phát hiện mặc định
        
        # Thiết lập mặc định: Làn 1 (Ô tô, Xe máy), Làn 2 (Xe buýt, Xe tải)
        self.lane_vehicle_types = {
            "Lane1": {"car": True, "motorcycle": True, "bus": False, "truck": False},
            "Lane2": {"car": False, "motorcycle": False, "bus": True, "truck": True}
        }

    def update_config(self, new_value):
        if new_value == "" or new_value.isdigit():
            self.config_value = new_value if new_value else "0"
            num_lanes = int(self.config_value) if self.config_value.isdigit() else 0
            if len(self.lane_vehicle_types) != num_lanes:
                self.lane_vehicle_types = {
                    f"Lane{i+1}": {vehicle: False for vehicle in self.vehicle_types}
                    for i in range(num_lanes)
                }

    def update_lane_vehicle(self, lane, vehicle_type, value):
        if lane in self.lane_vehicle_types:
            self.lane_vehicle_types[lane][vehicle_type] = value

    def update_detection_threshold(self, new_value):
        try:
            new_value = float(new_value)
            if 0 <= new_value <= 1:
                self.detection_threshold = new_value
            else:
                raise ValueError("Detection threshold must be between 0 and 1")
        except ValueError as e:
            print(f"Error updating detection threshold: {e}")

    def get_lane_vehicle_types(self):
        return self.lane_vehicle_types

    def get_num_lanes(self):
        return int(self.config_value) if self.config_value.isdigit() else 0

    def get_config(self):
        vehicle_class_map = {
            "car": 2, "motorcycle": 3, "bus": 5, "truck": 7
        }
        num_lanes = self.get_num_lanes()
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
                "allowed_vehicles": allowed_vehicles
            })
        return {
            "detection_threshold": self.detection_threshold,
            "num_lanes": num_lanes,
            "lanes": lanes
        }