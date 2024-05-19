# door.py
class Door:
    def __init__(self):
        self.is_closed = True

    def toggle_door(self):
        self.is_closed = not self.is_closed
