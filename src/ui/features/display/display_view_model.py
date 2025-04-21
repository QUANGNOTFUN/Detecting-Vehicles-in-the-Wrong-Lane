import random

class DisplayViewModel:
    def __init__(self):
        self.display_data = "Initial Data"

    def update_data(self):
        self.display_data = "Updated Data " + str(random.randint(1, 1000))