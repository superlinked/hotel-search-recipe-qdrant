import logging
import os
import json
from datetime import datetime

from app.config import settings


class JSONLFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.msg,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging():
    logger_name = "frontend"

    logger = logging.getLogger(logger_name)
    if logger.handlers:
        logger.debug(f"Logger '{logger_name}' is already initialized")
        return logger

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{logger_name}_{timestamp}.jsonl"
    log_filepath = os.path.join(log_dir, log_filename)

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.INFO)

    jsonl_formatter = JSONLFormatter()
    file_handler.setFormatter(jsonl_formatter)

    logger.addHandler(file_handler)

    logger.propagate = False

    level = settings.log_level.upper()
    logger.setLevel(level)

    return logger
