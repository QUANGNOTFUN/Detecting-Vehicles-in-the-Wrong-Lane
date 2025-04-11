import tkinter as tk
from src.view.main_view import MainView
from src.viewmodel.yolo_viewmodel import YoloViewModel
from src.model.yolo_model import YoloModel

if __name__ == "__main__":
    root = tk.Tk()
    model = YoloModel(model_path="assets/yolov8n.pt")
    viewmodel = YoloViewModel(model)
    app = MainView(root, viewmodel)
    root.mainloop()