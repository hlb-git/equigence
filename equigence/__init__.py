from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
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

from equigence import routes
from equigence import errors
