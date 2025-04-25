import dearpygui.dearpygui as dpg
import re

class ConfigScreen:
    def __init__(self, view_model):
        self.tag = "ConfigScreen"
        self.view_model = view_model
        self.grid_tag = "lane_vehicle_grid"
        self.input_tag = "lane_input"
        self.threshold_tag = "threshold_input"
        self.error_tag = "error_message"
        self.main_screen = None
        self.table_tag = "config_table"
        
        self.colors = {
            'header': (62, 146, 204),
            'text': (255, 255, 255),
            'error': (255, 82, 82),
            'success': (100, 255, 100),
            'highlight': (255, 191, 0),
            'button': (70, 163, 216),
            'table_header': (230, 230, 230),
            'table_header_text': (255, 255, 255),
            'table_row_even': (200, 200, 200),
            'table_row_odd': (255, 255, 255),
            'table_text': (255, 255, 255),
            'table_border': (255, 255, 255),
        }

    def create_table_theme(self):
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, self.colors['table_row_odd'])
                dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, self.colors['table_row_even'])
                dpg.add_theme_color(dpg.mvThemeCol_Text, self.colors['table_text'])
                
                dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, self.colors['table_header'])
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, self.colors['table_header'])
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, self.colors['table_header'])
                
                dpg.add_theme_color(dpg.mvThemeCol_Border, self.colors['table_border'])
                dpg.add_theme_color(dpg.mvThemeCol_Separator, self.colors['table_border'])
                
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 10, 5)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4)
                
            with dpg.theme_component(dpg.mvTableHeader):
                dpg.add_theme_color(dpg.mvThemeCol_Text, self.colors['table_header_text'])
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6)
                
            with dpg.theme_component(dpg.mvCheckbox):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 255, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (240, 240, 240))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (230, 230, 230))
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (0, 0, 0))
                
        return theme

    def on_lanes_changed(self, sender, app_data):
        if app_data == "" or app_data.isdigit():
            self.view_model.update_config(app_data)
            if dpg.does_item_exist(self.error_tag):
                dpg.delete_item(self.error_tag)
            self.update_ui()
        else:
            if not dpg.does_item_exist(self.error_tag):
                dpg.add_text("Chỉ được nhập số", color=(255, 0, 0), parent=self.input_tag, tag=self.error_tag)

    def on_threshold_changed(self, sender, app_data):
        self.view_model.update_detection_threshold(app_data)
        if dpg.does_item_exist(self.error_tag):
            dpg.delete_item(self.error_tag)

    def create_grid_button_callback(self, sender, app_data):
        if not self.view_model.config_value.isdigit():
            return
        
        num_lanes = int(self.view_model.config_value)
        if num_lanes <= 0 or num_lanes > 10:
            if not dpg.does_item_exist(self.error_tag):
                dpg.add_text("Số làn phải từ 1 đến 10", color=(255, 0, 0), parent=self.input_tag, tag=self.error_tag)
            return

        if dpg.does_item_exist(self.error_tag):
            dpg.delete_item(self.error_tag)

        self.update_ui()

    def checkbox_callback(self, sender, app_data, user_data):
        lane, vehicle_type = user_data
        self.view_model.update_lane_vehicle(lane, vehicle_type, app_data)

    def create_grid(self):
        if dpg.does_item_exist(self.grid_tag):
            dpg.delete_item(self.grid_tag)

        num_lanes = int(self.view_model.config_value)
        if num_lanes <= 0:
            return

        total_width = 655
        num_columns = len(self.view_model.vehicle_types) + 1
        column_width = 100

        with dpg.group(tag=self.grid_tag, parent=self.tag):
            dpg.add_text("Cấu hình loại xe cho từng làn đường:", color=(62, 146, 204))
            dpg.add_spacer(height=5)
            
            with dpg.table(header_row=True, 
                          row_background=True,
                          borders_innerH=True, 
                          borders_outerH=True, 
                          borders_innerV=True, 
                          borders_outerV=True,
                          width=total_width,
                          tag=self.table_tag):
                
                dpg.add_table_column(label="Làn đường", width_fixed=True, width=column_width, init_width_or_weight=column_width)
                for vehicle_type in self.view_model.vehicle_types:
                    vn_name = {
                        "car": "Ô tô con",
                        "motorcycle": "Xe máy",
                        "bus": "Xe buýt",
                        "truck": "Xe tải"
                    }.get(vehicle_type, vehicle_type)
                    dpg.add_table_column(label=vn_name, width_fixed=True, width=column_width, init_width_or_weight=column_width)

                for i in range(num_lanes):
                    lane_name = f"Lane{i+1}"
                    with dpg.table_row():
                        with dpg.group(horizontal=True):
                            text = f"Làn {i+1}"
                            text_width = dpg.get_text_size(text)[0] if dpg.get_text_size(text) else 0
                            padding = (column_width - text_width) // 2.5
                            dpg.add_spacer(width=padding)
                            dpg.add_text(text)
                        
                        for vehicle_type in self.view_model.vehicle_types:
                            with dpg.group(horizontal=True):
                                checkbox_width = 20
                                padding = (column_width - checkbox_width) // 2.5
                                dpg.add_spacer(width=padding)
                                is_checked = self.view_model.lane_vehicle_types.get(lane_name, {}).get(vehicle_type, False)
                                dpg.add_checkbox(
                                    default_value=is_checked,
                                    callback=self.checkbox_callback,
                                    user_data=(lane_name, vehicle_type)
                                )

    def update_ui(self):
        self.create_grid()

    def create(self):
        with dpg.group(horizontal=False, parent=self.tag):
            dpg.add_text("Cấu hình làn đường", color=(62, 146, 204))
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True, tag=self.input_tag):
                dpg.add_text("Số làn xe:", color=(255, 255, 255))
                dpg.add_input_text(
                    width=100,
                    decimal=True,
                    callback=self.on_lanes_changed,
                    default_value=self.view_model.config_value,
                    tag="lane_input_field"
                )
                dpg.add_spacer(width=20)
                dpg.add_text("Ngưỡng phát hiện:", color=(255, 255, 255))
                dpg.add_input_text(
                    width=100,
                    decimal=True,
                    callback=self.on_threshold_changed,
                    default_value=str(self.view_model.detection_threshold),
                    tag="threshold_input_field"
                )
                dpg.add_button(
                    label="Tạo bảng cấu hình",
                    callback=self.create_grid_button_callback,
                    width=150
                )