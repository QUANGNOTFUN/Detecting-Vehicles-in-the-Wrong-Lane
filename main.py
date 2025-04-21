# app.py
from src.ui.base.main_screen import MainScreen
from src.ui.base.main_view_model import MainViewModel

if __name__ == "__main__":
    # Tạo ViewModel cho MainScreen
    main_view_model = MainViewModel()
    
    # Tạo MainScreen và chạy ứng dụng
    app = MainScreen(main_view_model)
    app.run()