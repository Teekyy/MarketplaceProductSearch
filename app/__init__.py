from flask import Flask
from dotenv import load_dotenv
from utils.logger import setup_logger, logger
import logging
import os
from .extensions import mongo
from .custom_json_encoder import CustomJSONEncoder
from app.api.books import books_api


def create_app():
    load_dotenv()

    # Setup logger
    setup_logger(
        log_level=getattr(logging, os.getenv('LOG_LEVEL')),
        log_file=os.getenv('LOG_FILE')
    )

    # Create Flask app
    logger.info("Creating Sci-Fi Book Catalog Flask app")
    app = Flask(__name__)

    # Configure DB
    logger.info("Configuring MongoDB")
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    mongo.init_app(app)

    # Setup API
    logger.info("Setting up API")
    app.register_blueprint(books_api)

    # Setup JSON encoder
    logger.info("Setting up custom JSON encoder")
    app.json = CustomJSONEncoder(app)

    
    return app