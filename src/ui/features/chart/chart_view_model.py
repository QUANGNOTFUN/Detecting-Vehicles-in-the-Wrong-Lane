import csv
from datetime import datetime

class ChartViewModel:
    def __init__(self, csv_file="violations/violations.csv"):
        self.csv_file = csv_file
        # Danh sách các loại phương tiện
        self.vehicle_types = ["xe may", "oto", "xe tai", "xe bus"]
        # Ánh xạ từ tên phương tiện trong CSV sang loại phương tiện
        self.vehicle_type_map = {
            "Xe máy": "xe may",
            "Ô tô": "oto",
            "Xe tải": "xe tai",
            "Xe buýt": "xe bus"
        }
        # Khởi tạo dữ liệu ban đầu
        self.hourly_violations = [0] * 24  # Số lượng vi phạm theo giờ (0-23h)
        self.vehicle_counts = [0] * len(self.vehicle_types)  # Số lượng xe vi phạm theo loại
        self.load_data_from_csv()

    def load_data_from_csv(self):
        # Đặt lại dữ liệu trước khi tính toán
        self.hourly_violations = [0] * 24
        self.vehicle_counts = [0] * len(self.vehicle_types)

        try:
            with open(self.csv_file, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Lấy thời gian vi phạm và loại phương tiện
                    timestamp_str = row["Timestamp"]
                    vehicle_type = row["Vehicle Type"]

                    # Phân tích thời gian để lấy giờ
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    hour = timestamp.hour
                    self.hourly_violations[hour] += 1

                    # Đếm số lượng xe theo loại phương tiện
                    vehicle_category = self.vehicle_type_map.get(vehicle_type, None)
                    if vehicle_category:
                        idx = self.vehicle_types.index(vehicle_category)
                        self.vehicle_counts[idx] += 1

        except FileNotFoundError:
            print(f"File {self.csv_file} không tồn tại, sử dụng dữ liệu mặc định.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")

    def refresh_chart(self):
        # Tải lại dữ liệu từ CSV khi làm mới biểu đồ
        self.load_data_from_csv()