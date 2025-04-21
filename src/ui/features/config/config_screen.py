import dearpygui.dearpygui as dpg

class ConfigScreen:
    def __init__(self, view_model):
        self.tag = "ConfigScreen"
        self.view_model = view_model
        self.main_screen = None

    def create(self):
        dpg.add_text("This is the Configuration Screen!")
        dpg.add_text(f"Config: {self.view_model.config_value}", tag="config_value")
        dpg.add_input_text(label="Update Config", callback=self.update_config)
        dpg.add_button(label="Back to Main", callback=lambda: self.main_screen.show_frame("MainScreen"))

    def show(self):
        dpg.configure_item(self.tag, show=True)
        self.update_ui()

    def hide(self):
        dpg.configure_item(self.tag, show=False)

    def update_ui(self):
        dpg.set_value("config_value", f"Config: {self.view_model.config_value}")

    def update_config(self, sender, app_data):
        self.view_model.update_config(app_data)
        self.update_ui()