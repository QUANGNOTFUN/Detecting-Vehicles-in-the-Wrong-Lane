import dearpygui.dearpygui as dpg

class DisplayScreen:
    def __init__(self, view_model):
        self.tag = "DisplayScreen"
        self.view_model = view_model
        self.main_screen = None

    def create(self):
        # Nội dung màn hình Display
        dpg.add_text("This is the Display Screen!")
        dpg.add_text(f"Display Data: {self.view_model.display_data}", tag="display_data")
        dpg.add_button(label="Update Data", callback=self.update_data)

    def update_ui(self):
        dpg.set_value("display_data", f"Display Data: {self.view_model.display_data}")

    def update_data(self):
        self.view_model.update_data()
        self.update_ui()