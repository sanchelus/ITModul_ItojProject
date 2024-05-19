from flask import Flask, render_template, redirect, url_for, request
from flask_pymongo import PyMongo
from pymongo import MongoClient
from house import House
from security import SecuritySystem
from fire_alarm import FireAlarm
from room import Room
from data_analyzer import DataAnalyzer
import json

with open('rooms.json') as f:
    data = json.load(f)

house = House()
for room_info in data['rooms']:
    room = Room(room_info['name'])
    room.light = room_info['light']
    room.temperature = room_info['temperature']
    house.add_room(room)

app = Flask(__name__)
app.config.from_pyfile('config.py')
mongo = PyMongo(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['smart_home']
state_collection = db['state']

security_system = SecuritySystem()
fire_alarm = FireAlarm()

@app.route('/')
def home():
    analyzer = DataAnalyzer('rooms')
    analysis_results = analyzer.analyze()
    return render_template('index.html', house=house, security_system=security_system, fire_alarm=fire_alarm, analysis_results=analysis_results)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        room_name = request.form['room']
        temperature = int(request.form['temperature'])
        light = 'light' in request.form
        room = house.get_room_by_name(room_name)
        if room:
            room.set_temperature(temperature)
            room.light = light
            state_collection.update_one({'name': room_name}, {'$set': {'temperature': temperature, 'light': light}}, upsert=True)
    return render_template('admin.html', house=house, security_system=security_system, fire_alarm=fire_alarm)

@app.route('/toggle_light/<room_name>')
def toggle_light(room_name):
    room = house.get_room_by_name(room_name)
    if room:
        room.toggle_light()
        state_collection.update_one({'name': room_name}, {'$set': {'light': room.light}}, upsert=True)
    return redirect(url_for('admin_panel'))

@app.route('/turn_on_all_lights')
def turn_on_all_lights():
    for room in house.rooms:
        room.light = True
        state_collection.update_one({'name': room.name}, {'$set': {'light': True}}, upsert=True)
    return redirect(url_for('admin_panel'))

@app.route('/turn_off_all_lights')
def turn_off_all_lights():
    for room in house.rooms:
        room.light = False
        state_collection.update_one({'name': room.name}, {'$set': {'light': False}}, upsert=True)
    return redirect(url_for('admin_panel'))

@app.route('/toggle_alarm')
def toggle_alarm():
    security_system.toggle_alarm()
    state_collection.update_one({'name': 'security_system'}, {'$set': {'alarm_on': security_system.alarm_on}}, upsert=True)
    return redirect(url_for('admin_panel'))

@app.route('/toggle_door')
def toggle_door():
    house.door.toggle_door()
    state_collection.update_one({'name': 'door'}, {'$set': {'is_closed': house.door.is_closed}}, upsert=True)
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
