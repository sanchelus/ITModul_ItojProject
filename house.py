# house.py
from door import Door

class House:
    def __init__(self):
        self.rooms = []
        self.door = Door()  # Добавляем объект двери

    def add_room(self, room):
        self.rooms.append(room)

    def get_room_by_name(self, name):
        for room in self.rooms:
            if room.name == name:
                return room
        return None
