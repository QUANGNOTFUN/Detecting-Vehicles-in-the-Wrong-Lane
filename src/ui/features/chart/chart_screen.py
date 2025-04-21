import dearpygui.dearpygui as dpg

class ChartScreen:
    def __init__(self, view_model):
        self.tag = "ChartScreen"
        self.view_model = view_model
        self.main_screen = None

    def create(self):
        dpg.add_text("This is the Chart Screen!")
        dpg.add_text(f"Chart Data: {self.view_model.chart_data}", tag="chart_data")
        dpg.add_button(label="Refresh Chart", callback=self.refresh_chart)
        dpg.add_button(label="Back to Main", callback=lambda: self.main_screen.show_frame("MainScreen"))

    def show(self):
        dpg.configure_item(self.tag, show=True)
        self.update_ui()

    def hide(self):
        dpg.configure_item(self.tag, show=False)

    def update_ui(self):
        dpg.set_value("chart_data", f"Chart Data: {self.view_model.chart_data}")

    def refresh_chart(self):
        self.view_model.refresh_chart()
        self.update_ui()