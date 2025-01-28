from flask import Flask
from dotenv import load_dotenv
import os
from .extensions import mongo
from .custom_json_encoder import CustomJSONEncoder
from app.api.books import books_api


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')

    mongo.init_app(app)
    
    app.json = CustomJSONEncoder(app)

    app.register_blueprint(books_api)

    return app