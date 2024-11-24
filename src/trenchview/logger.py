import logging
from logging.handlers import RotatingFileHandler
import sys


def setup_logging(log_level, log_file=None):
    """Configure logging for both file and console output"""
    # Create logger with a namespace that matches your application
    logger = logging.getLogger("trenchview")
    logger.setLevel(log_level)

    # Prevent duplicate logs by checking if handlers already exist
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=1024 * 1024, backupCount=3
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger