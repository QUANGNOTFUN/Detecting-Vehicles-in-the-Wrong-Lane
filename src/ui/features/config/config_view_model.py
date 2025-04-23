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