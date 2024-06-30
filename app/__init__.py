from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from .custom_json_encoder import CustomJSONEncoder

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo = PyMongo(app)

db = mongo.cx['marketplace']

app.json = CustomJSONEncoder(app)

from app import routes