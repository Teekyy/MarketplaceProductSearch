from app import create_app
from utils.logger import setup_logger, logging
from dotenv import load_dotenv
import os
from app.config import Config

if __name__ == '__main__':
    load_dotenv()

    # Setup logger
    setup_logger(
        log_level=getattr(logging, os.getenv('LOG_LEVEL')),
        log_file=os.getenv('LOG_FILE')
    )

    app = create_app(Config)

    # Configure Flask run environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    app.run(debug=debug_mode, host=host, port=port)