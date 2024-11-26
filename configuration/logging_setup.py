import logging
import os
from logging.config import dictConfig
from os import getcwd

logger = logging.getLogger("Kameleon")
logging_path = f"{getcwd()}/logs"
if not os.path.exists(logging_path):
    os.mkdir(logging_path)


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "core.loggers.ColorFormatter",
            "format": "[%(asctime)s | %(levelname)s] module:%(module)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "()": "core.loggers.ColorFormatter",
            "format": "[%(asctime)s | %(levelname)s | line:%(lineno)d] | %(name)s | %(module)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "detailed",
            "filename": f"{logging_path}/kameleon-error.log",
            "maxBytes": 1000000,
            "backupCount": 3,
        },
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["stdout", "file"]},
                "werkzeug": {"level": "INFO", "propagate": True},
                "pssh": {"level": "WARNING", "propagate": True},
                "schedule": {"level": "WARNING", "propagate": True},
                "urllib3": {"level": "WARNING", "propagate": True}
                },
}


def setup_logging():
    dictConfig(config=logging_config)
