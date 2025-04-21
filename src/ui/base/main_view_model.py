class MainViewModel:
    def __init__(self):
        self.message = "Hello from MainViewModel!"

    def update_message(self, new_message):
        self.message = new_message