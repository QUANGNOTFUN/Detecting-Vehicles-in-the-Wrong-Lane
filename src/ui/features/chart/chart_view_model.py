import random

class ChartViewModel:
    def __init__(self):
        # Data for the line chart: violations by hour (24 hours)
        self.hourly_violations = [random.randint(0, 50) for _ in range(24)]
        # Data for the bar chart: vehicle types and their counts
        self.vehicle_types = ["xe may", "xe o to", "xe tai", "xe bus", "xe dau keo"]
        self.vehicle_counts = [random.randint(10, 100) for _ in range(len(self.vehicle_types))]

    def refresh_chart(self):
        # Refresh data for the line chart
        self.hourly_violations = [random.randint(0, 50) for _ in range(24)]
        # Refresh data for the bar chart
        self.vehicle_counts = [random.randint(10, 100) for _ in range(len(self.vehicle_types))]
