# logging_setup.py

import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logging():
    # Configure logging with TimedRotatingFileHandler
    log_handler = TimedRotatingFileHandler('watchdog.log', when='midnight', interval=1)
    log_handler.suffix = "%Y-%m-%d"  # Use date format for the log file suffix
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)

    # Set up the logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)

    # Add console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

