import dearpygui.dearpygui as dpg

class ChartScreen:
    def __init__(self, view_model):
        self.tag = "ChartScreen"
        self.view_model = view_model
        self.main_screen = None
        # Tags for dynamically updating the charts
        self.line_series_tag = "line_series"
        self.bar_series_tag = "bar_series"

    def create(self):
        # Group to hold both charts side by side
        with dpg.group(horizontal=True):
            # Left Chart: Line Chart for Violations by Hour
            with dpg.group():
                dpg.add_text("Biểu đồ số lượng xe vi phạm theo giờ")  # Chart title
                with dpg.plot(label="Số lượng xe", height=300, width=400):
                    dpg.add_plot_axis(dpg.mvXAxis, label="Giờ")
                    with dpg.plot_axis(dpg.mvYAxis, label="Số lượng xe"):
                        # Use view_model.hourly_violations for the line chart
                        hours = list(range(24))  # 0 to 23 hours
                        dpg.add_line_series(hours, self.view_model.hourly_violations, label="Vi phạm", tag=self.line_series_tag)

            # Right Chart: Bar Chart for Vehicle Types
            with dpg.group():
                dpg.add_text("Biểu đồ thống kê số lượng xe theo loại trong ngày")  # Chart title
                with dpg.plot(label="Số lượng xe", height=300, width=400):
                    x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Loại xe")
                    with dpg.plot_axis(dpg.mvYAxis, label="Số lượng xe"):
                        # Use view_model.vehicle_counts for the bar chart
                        x_positions = list(range(len(self.view_model.vehicle_types)))  # [0, 1, 2, 3, 4]
                        dpg.add_bar_series(x_positions, self.view_model.vehicle_counts, label="Số lượng", tag=self.bar_series_tag)
                # Add a manual label below the chart to indicate vehicle types
                labels_text = " ".join([f"{i}: {label}" for i, label in enumerate(self.view_model.vehicle_types)])
                dpg.add_text(labels_text)

        # Bottom Buttons (Refresh Chart, Back to Main)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh Chart", callback=self.refresh_chart)
            dpg.add_button(label="Back to Main", callback=lambda: self.main_screen.show_frame("MainScreen"))

    def show(self):
        dpg.configure_item(self.tag, show=True)
        self.update_ui()

    def hide(self):
        dpg.configure_item(self.tag, show=False)

    def update_ui(self):
        # Update the line chart with new data from view_model
        hours = list(range(24))
        dpg.set_value(self.line_series_tag, [hours, self.view_model.hourly_violations])

        # Update the bar chart with new vehicle data
        x_positions = list(range(len(self.view_model.vehicle_types)))
        dpg.set_value(self.bar_series_tag, [x_positions, self.view_model.vehicle_counts])

    def refresh_chart(self):
        # Refresh the data
        self.view_model.refresh_chart()
        self.update_ui()
