import random

class ChartViewModel:
    def __init__(self):
        self.chart_data = [random.randint(1, 100) for _ in range(5)]

    def refresh_chart(self):
        self.chart_data = [random.randint(1, 100) for _ in range(5)]