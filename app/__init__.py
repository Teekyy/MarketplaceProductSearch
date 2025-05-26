from flask import Flask, current_app
from utils.logger import logger
from app.config import Config
from .custom_json_encoder import CustomJSONEncoder
from pymongo import MongoClient


def create_app(config_class=Config):
    # Create Flask app
    logger.info("Creating Sci-Fi Book Catalog Flask app")
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure DB
    logger.info("Configuring MongoDB")
    init_db(app)

    # Setup API
    logger.info("Setting up API")
    from app.api.books import books_api
    app.register_blueprint(books_api)

    # Setup JSON encoder
    logger.info("Setting up custom JSON encoder")
    app.json = CustomJSONEncoder(app)

    return app


def init_db(app):
    """
    Initialize the MongoDB database connection.
    """
    # Store database connection on app instance
    app.mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = app.mongo_client[app.config['MONGO_DB']]

    # Create indexes
    app.db.books.create_index({ "isbn_13": 1}, unique=True)

    # Close database connection on app exit
    import atexit
    atexit.register(lambda: app.mongo_client.close())


def get_db():
    """
    Get the database instance from the current Flask app context.
    """
    if not hasattr(current_app, 'db'):
        logger.error("Database not initialized")
        raise RuntimeError("Database not initialized. Please call init_db() first.")
    return current_app.db
    