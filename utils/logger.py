import logging
from logging.handlers import RotatingFileHandler
import sys
import os

logger = logging.getLogger('Scifi Catalog')

def setup_logger(log_level=logging.INFO, log_file='logs/app.log'):
    """
    Sets up the logger configuration.
    """
    # Create log directory if passed and it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set log level
    logger.setLevel(log_level)

    # Create file and console handlers
    # 10 MiB (binary megabytes) per file
    fh = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    ch = logging.StreamHandler(sys.stdout)

    # Create formatter and apply to handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger