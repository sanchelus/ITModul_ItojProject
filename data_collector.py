import time
from datetime import datetime
from pymongo import MongoClient

class DataCollector:
    def __init__(self, house):
        self.house = house
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['smart_home']
        self.collection = self.db['state']

    def collect_data(self):
        while True:
            for room in self.house.rooms:
                data = {
                    'room_name': room.name,
                    'temperature': room.temperature,
                    'light': room.light,
                    'timestamp': datetime.now().isoformat()
                }
                if validate_data(data):
                    self.collection.insert_one(data)
                else:
                    print(f"Invalid data: {data}")

            # Данные о состоянии двери
            door_data = {
                'door_state': self.house.door.is_closed,
                'timestamp': datetime.now().isoformat()
            }
            if validate_data(door_data):
                self.collection.insert_one(door_data)

            # Данные о состоянии системы безопасности
            security_data = {
                'alarm_on': self.house.security_system.alarm_on,
                'timestamp': datetime.now().isoformat()
            }
            if validate_data(security_data):
                self.collection.insert_one(security_data)

            # Данные о состоянии пожарной сигнализации
            fire_alarm_data = {
                'fire_detected': self.house.fire_alarm.fire_detected,
                'timestamp': datetime.now().isoformat()
            }
            if validate_data(fire_alarm_data):
                self.collection.insert_one(fire_alarm_data)

            # Ожидание следующего цикла сбора данных
            time.sleep(60)

def validate_data(data):
    # Проверка типа данных
    if 'temperature' in data and not isinstance(data['temperature'], (int, float)):
        return False
    if 'light' in data and not isinstance(data['light'], bool):
        return False
    if 'timestamp' in data and not isinstance(data['timestamp'], str):
        return False
    if 'room_name' in data and not isinstance(data['room_name'], str):
        return False
    if 'door_state' in data and not isinstance(data['door_state'], bool):
        return False
    if 'alarm_on' in data and not isinstance(data['alarm_on'], bool):
        return False
    if 'fire_detected' in data and not isinstance(data['fire_detected'], bool):
        return False

    # Проверка диапазона значений
    if 'temperature' in data and not (-30 <= data['temperature'] <= 50):
        return False

    # Проверка целостности данных
    if 'timestamp' not in data:
        return False
    if 'room_name' in data and not data['room_name']:
        return False

    return True
