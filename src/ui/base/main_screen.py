# src/ui/base/main_screen.py
import dearpygui.dearpygui as dpg
from src.ui.features.config.config_screen import ConfigScreen
from src.ui.features.config.config_view_model import ConfigViewModel
from src.ui.features.chart.chart_screen import ChartScreen
from src.ui.features.chart.chart_view_model import ChartViewModel
from src.ui.features.display.display_screen import DisplayScreen
from src.ui.features.display.display_view_model import DisplayViewModel

class MainScreen:
    def __init__(self, view_model):
        self.tag = "main_window"
        self.view_model = view_model
        self.screens = {}
        
        # Khởi tạo DPG context
        dpg.create_context()

    def setup_theme(self):
        # Tạo theme mặc định
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Màu chữ mặc định
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
                # Màu nền cửa sổ
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
                # Màu nền menu
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (40, 40, 40))
                # Màu button
                dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 90))

        # Áp dụng theme mặc định
        dpg.bind_theme(global_theme)

        # Tạo font registry
        with dpg.font_registry():
            # Font cho tiêu đề (size 24)
            with dpg.font("assets/fonts/Roboto-Bold.ttf", 24) as title_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            self.title_font = title_font

            # Font cho menu (size 20)
            with dpg.font("assets/fonts/Roboto-Medium.ttf", 20) as menu_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            self.menu_font = menu_font

            # Font mặc định (size 18)
            with dpg.font("assets/fonts/Roboto-Regular.ttf", 18) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.bind_font(default_font)

    def button_callback(self, sender, app_data, user_data):
        self.show_frame(user_data)

    def create(self):
        # Tạo viewport với kích thước lớn hơn
        dpg.create_viewport(
            title="WRONG LANE VEHICLE DETECTION SYSTEM", 
            width=1280, height=720
        )

        # Thiết lập theme và font
        self.setup_theme()

        # Tạo các ViewModel cho các màn hình tính năng
        display_view_model = DisplayViewModel()
        chart_view_model = ChartViewModel()
        config_view_model = ConfigViewModel()

        # Tạo các màn hình
        display_screen = DisplayScreen(display_view_model)
        chart_screen = ChartScreen(chart_view_model)
        config_screen = ConfigScreen(config_view_model)

        # Lưu các màn hình vào dictionary
        self.screens = {
            "DisplayScreen": display_screen,
            "ChartScreen": chart_screen,
            "ConfigScreen": config_screen
        }

        # Gán tham chiếu MainScreen cho các màn hình
        for screen in self.screens.values():
            screen.main_screen = self

        # Tạo window chính
        with dpg.window(
            label="WRONG LANE VEHICLE DETECTION SYSTEM", 
            tag=self.tag,
            width=1000, height=500
        ):
            # Menu Bar
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

            # Tạo các group cho từng màn hình
            for screen_name, screen in self.screens.items():
                with dpg.group(tag=screen_name, show=False):
                    screen.create()

    def show_frame(self, frame_tag):
        # Ẩn tất cả các màn hình
        for screen_name in self.screens:
            dpg.configure_item(screen_name, show=False)

        # Hiển thị màn hình được chọn
        dpg.configure_item(frame_tag, show=True)

    def run(self):
        # Tạo các màn hình và giao diện
        self.create()

        # Thiết lập DPG sau khi giao diện đã được tạo
        dpg.setup_dearpygui()

        # Hiển thị màn hình mặc định (DisplayScreen)
        self.show_frame("DisplayScreen")

        # Hiển thị viewport và bắt đầu vòng lặp chính
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()