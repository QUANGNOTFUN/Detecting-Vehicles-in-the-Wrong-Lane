import tkinter as tk
from src.model.yolo_model import YoloModel
from src.viewmodel.yolo_viewmodel import YoloViewModel
from src.view.main_view import MainView
from src.view.report_screen import ReportScreen

if __name__ == "__main__":
    root = tk.Tk()
    model = YoloModel(model_path="assets/yolov8n.pt")
    viewmodel = YoloViewModel(model)
    app = MainView(root, viewmodel)
    root.mainloop()