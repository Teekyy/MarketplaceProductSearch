from flask import Flask, current_app
from utils.logger import logger
from app.config import Config
from .custom_json_encoder import CustomJSONEncoder
from pymongo import MongoClient
from app.services import S3Service, BookService


def create_app(config_class=Config):
    """
    Create a Flask application instance with the given configuration class.

    Args:
        config_class (Config): The configuration class to use for the Flask app.
    
    Returns:
        Flask: The configured Flask application instance.
    """

    # Create Flask app
    logger.info("Creating Sci-Fi Book Catalog Flask app")
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure DB
    logger.info("Configuring MongoDB")
    init_db(app)

    # Configure Services
    init_services(app)

    # Setup API
    logger.info("Setting up API")
    from app.api.books import books_api
    app.register_blueprint(books_api)

    # Setup JSON encoder
    logger.info("Setting up custom JSON encoder")
    app.json = CustomJSONEncoder(app)

    return app


def init_services(app):
    """
    Initialize the services used by the application.

    Args:
        app (Flask): The Flask application instance.
    """
    # Create services
    s3_service = S3Service(
        bucket_name=app.config["AWS_BUCKET_NAME"],
        region_name=app.config["AWS_REGION"],
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"]
    )

    book_service = BookService(app.db, s3_service)

    # Register services in app
    app.s3_service = s3_service
    app.book_service = book_service


def init_db(app):
    """
    Initialize the MongoDB database connection.

    Args:
        app (Flask): The Flask application instance.
    """
    # Store database connection on app instance
    app.mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = app.mongo_client[app.config['MONGO_DB']]

    # Create indexes
    app.db.books.create_index({ "isbn_13": 1}, unique=True)

    # Close database connection on app exit
    import atexit
    atexit.register(lambda: app.mongo_client.close())
    