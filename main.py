import dearpygui.dearpygui as dpg
from src.model.yolo_model import YoloModel
from feature.display.displayViewmodel import YoloViewModel
from base.mainScreen import MainScreen

if __name__ == "__main__":

    model = YoloModel(model_path="assets/yolov8n.pt")

    viewmodel = YoloViewModel(model)

    app = MainScreen(viewmodel)
    
    app.run()