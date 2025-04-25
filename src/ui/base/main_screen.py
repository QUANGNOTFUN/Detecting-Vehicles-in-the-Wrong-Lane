# src/ui/base/main_screen.py
import dearpygui.dearpygui as dpg
from src.ui.features.config.config_screen import ConfigScreen
from src.ui.features.config.config_view_model import ConfigViewModel
from src.ui.features.chart.chart_screen import ChartScreen
from src.ui.features.chart.chart_view_model import ChartViewModel
from src.ui.features.display.display_screen import DisplayScreen
from src.ui.features.display.display_view_model import DisplayViewModel
from src.ui.base.main_view_model import MainViewModel

class MainScreen:
    def __init__(self, view_model):
        self.tag = "main_window"
        self.view_model = view_model
        self.screens = {}
        self.config_view_model = ConfigViewModel()  # Khởi tạo ConfigViewModel
        
        # Khởi tạo DPG context
        dpg.create_context()

    def setup_theme(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 90))
        dpg.bind_theme(global_theme)

        with dpg.font_registry():
            with dpg.font("assets/fonts/Roboto-Bold.ttf", 24) as title_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            self.title_font = title_font

            with dpg.font("assets/fonts/Roboto-Medium.ttf", 20) as menu_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            self.menu_font = menu_font

            with dpg.font("assets/fonts/Roboto-Regular.ttf", 18) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.bind_font(default_font)

    def button_callback(self, sender, app_data, user_data):
        self.show_frame(user_data)

    def create(self):
        dpg.create_viewport(
            title="WRONG LANE VEHICLE DETECTION SYSTEM", 
            width=1280, height=720
        )

        self.setup_theme()

        display_view_model = DisplayViewModel()
        chart_view_model = ChartViewModel()
        config_view_model = self.config_view_model

        display_screen = DisplayScreen(display_view_model, config_view_model)
        chart_screen = ChartScreen(chart_view_model)
        config_screen = ConfigScreen(config_view_model)

        self.screens = {
            "DisplayScreen": display_screen,
            "ChartScreen": chart_screen,
            "ConfigScreen": config_screen
        }

        for screen in self.screens.values():
            screen.main_screen = self

        with dpg.window(
            label="WRONG LANE VEHICLE DETECTION SYSTEM", 
            tag=self.tag,
            width=1000, height=500
        ):
            with dpg.menu_bar():
                menu_items = [
                    ("Display", "DisplayScreen"),
                    ("Chart", "ChartScreen"),
                    ("Config", "ConfigScreen")
                ]
                
                for label, screen in menu_items:
                    button = dpg.add_button(
                        label=label,
                        callback=self.button_callback,
                        user_data=screen
                    )
                    dpg.bind_item_font(button, self.menu_font)

            for screen_name, screen in self.screens.items():
                with dpg.group(tag=screen_name, show=False):
                    screen.create()

    def show_frame(self, frame_tag):
        for screen_name in self.screens:
            dpg.configure_item(screen_name, show=False)

        dpg.configure_item(frame_tag, show=True)
        # Gọi update_ui() cho ConfigScreen sau khi show
        if frame_tag == "ConfigScreen":
            self.screens["ConfigScreen"].update_ui()

    def run(self):
        self.create()
        dpg.setup_dearpygui()
        self.show_frame("DisplayScreen")
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()