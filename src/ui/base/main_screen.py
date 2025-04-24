import dearpygui.dearpygui as dpg

class MainScreen:
    def __init__(self, view_model):
        self.tag = "main_window"
        self.view_model = view_model
        self.screens = {}
        
        # Khởi tạo DPG context
        dpg.create_context()
        
        # Tạo viewport
        dpg.create_viewport(title='WRONG LANE VEHICLE DETECTION SYSTEM', width=1200, height=600)
        
        # Tạo cửa sổ điều khiển với nút "Thêm Nút"
        with dpg.window(label="Control Window", width=200, height=100, pos=(0, 0)):
            dpg.add_button(label="Thêm Nút", callback=self._add_button_callback)

    def setup_theme(self):
        # Tạo theme mặc định
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (40, 40, 40))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 50))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 70))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 90))
        dpg.bind_theme(global_theme)

        # Tạo font registry
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
        self.setup_theme()
        
        # Tạo cửa sổ chính
        with dpg.window(
            label="WRONG LANE VEHICLE DETECTION SYSTEM",
            tag=self.tag,
            width=1000, height=500, pos=(200, 100)
        ):
            dpg.add_text("Chào mừng đến với hệ thống phát hiện xe đi sai làn!")
            dpg.add_button(label="Nhấn tôi", callback=self._button_callback)
            dpg.add_input_text(label="Nhập văn bản", default_value="Nhập gì đó...")

    def show_frame(self, frame_tag):
        for screen_name in self.screens:
            dpg.configure_item(screen_name, show=False)
        if frame_tag in self.screens:
            dpg.configure_item(frame_tag, show=True)

    def add_display(self):
        self.create()

    def _button_callback(self):
        print("Nút đã được nhấn!")

    def _add_button_callback(self):
        print("Nút Thêm đã được nhấn!")
        # Tạo cửa sổ chính mới
        new_tag = f"main_window_{len(self.screens) + 1}"
        with dpg.window(
            label="WRONG LANE VEHICLE DETECTION SYSTEM",
            tag=new_tag,
            width=1000, height=500, pos=(200 + len(self.screens) * 20, 100 + len(self.screens) * 20)
        ):
            dpg.add_text("Chào mừng đến với hệ thống phát hiện xe đi sai làn!")
            dpg.add_button(label="Nhấn tôi", callback=self._button_callback)
            dpg.add_input_text(label="Nhập văn bản", default_value="Nhập gì đó...")
        self.screens[new_tag] = True

    def run(self):
        self.create()
        dpg.setup_dearpygui()
        self.show_frame(self.tag)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
