import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# TODO: Implement notification
def notification(msg: str) -> None:
    print(f'--Notification-- {msg}')

class NotificationHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            try:
                notification(self.format(record))
            except Exception as e:
                # Log to stderr or fallback logger if notification fails
                logging.getLogger(__name__).error("Notification handler failed", exc_info=True)


def setup_logging(name: str = __name__) -> logging.Logger:
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    LOG_DIR = Path('logs')
    LOG_DIR.mkdir(exist_ok=True)
    (LOG_DIR / name).mkdir(exist_ok=True)

    LOG_FILE_PATH = LOG_DIR / name / 'pipeline.log'
    ERROR_LOG_FILE_PATH = LOG_DIR / name / 'error.log'

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOGGING_LEVEL))
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # General file handler
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

        # Error file handler
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE_PATH, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)

        # Notification handler
        notification_handler = NotificationHandler()
        notification_handler.setFormatter(formatter)
        notification_handler.setLevel(logging.ERROR)
        logger.addHandler(notification_handler)

    return logger

