class ConfigViewModel:
    def __init__(self):
        self.config_value = "Default Config"

    def update_config(self, new_value):
        self.config_value = new_value