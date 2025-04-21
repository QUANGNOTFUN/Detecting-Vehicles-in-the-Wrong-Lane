import dearpygui.dearpygui as dpg
from src.model.yolo_model import YoloModel
from src.viewmodel.yolo_viewmodel import YoloViewModel
from src.view.main_screen import MainScreen

if __name__ == "__main__":

    model = YoloModel(model_path="assets/yolov8n.pt")

    viewmodel = YoloViewModel(model)

    app = MainScreen(viewmodel)
    
    app.run()