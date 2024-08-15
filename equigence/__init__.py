from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from equigence.states_and_towns import states_and_towns
import gridfs



app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = 'fc8f3aa817427b9a83648d17332fab8484fc1f'
app.config["MONGO_URI"] = "mongodb://localhost:27017/equigence"
db = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
fs = gridfs.GridFS(db.cx.equigence)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


state_dropdown = [(state, state) for state in states_and_towns.keys()]
state_dropdown = [('', '(Select State)')] + state_dropdown

"""
# This code snippet is used to get the states and towns from the API
import requests

state_url = "https://nigeria-states-towns-lga.onrender.com/api/states"
all_url = "https://nigeria-states-towns-lga.onrender.com/api/all"

all_data = requests.get(all_url).json()
states_data = requests.get(state_url).json()

states_and_towns = {}


for state in states_data:
    current_state = state.get('name')
    towns = []
    for state_name in all_data:
        for town in state_name.get('towns'):
            if state_name.get('name') == current_state:
                towns.append(town.get('name'))
    states_and_towns[current_state] = towns

"""

from equigence import routes
from equigence import errors
