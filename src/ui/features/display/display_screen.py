import dearpygui.dearpygui as dpg
from src.ui.features.display.display_view_model import DisplayViewModel

class DisplayScreen:
    def __init__(self, view_model: DisplayViewModel):
        self.view_model = view_model
        self.main_screen = None  # Will be set by MainScreen
        self.display_count = 1  # Start from 1

    def create_display_panel(self, label, tag_prefix):
        with dpg.group(tag=tag_prefix, horizontal=False):
            # Tab buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label=label, width=100, callback=lambda: self.update_ui(tag_prefix))
                dpg.add_button(label="Report chart", width=110)
                dpg.add_button(label="Config Lane", width=110)

            dpg.add_spacer(height=5)

            # Display area
            dpg.add_child_window(tag=f"{tag_prefix}_screen", width=540, height=350, border=True)
            with dpg.drawlist(width=540, height=350, parent=f"{tag_prefix}_screen"):
                dpg.draw_rectangle((0, 0), (540, 350), color=(0, 0, 0, 255), fill=(0, 0, 0, 255))

            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start camera", width=110)
                dpg.add_button(label="Load", width=110)
                dpg.add_button(label="Stop", width=110)
                dpg.add_button(label="Exit", width=110)

    def create(self):
        # Create a child window with horizontal scrollbar to hold all display panels
        with dpg.child_window(parent="DisplayScreen", width=-1, height=-1, horizontal_scrollbar=True):
            with dpg.group(horizontal=True, tag="display_container"):
                # Initial display panel (Display 1)
                with dpg.group():
                    self.create_display_panel("Display 1", "display1")

        dpg.add_spacer(height=10, parent="DisplayScreen")
        dpg.add_button(label="New Camera", width=130, height=50, callback=self.add_new_display, parent="DisplayScreen")

    def add_new_display(self):
        self.display_count += 1
        tag_prefix = f"display{self.display_count}"
        label = f"Display {self.display_count}"

        # Add new display panel to the existing horizontal group "display_container"
        with dpg.group(parent="display_container"):
            self.create_display_panel(label, tag_prefix)

    def update_ui(self, tag_prefix):
        self.view_model.update_data()
        print(f"[{tag_prefix}] Data updated: {self.view_model.display_data}")
