import atexit
import os
import queue
from logging.config import dictConfig
import logging
from logging.handlers import QueueHandler, QueueListener
from os import getcwd

logger = logging.getLogger("Kameleon")
logging_path = f"{getcwd()}/logs"
if not os.path.exists(logging_path):
    os.mkdir(logging_path)


def get_handler_by_name(name):
    logger = logging.getLogger("")
    for handler in logger.handlers:
        if handler.name == name:
            return handler
    return None


logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s | %(levelname)s] module:%(module)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '[%(asctime)s | %(levelname)s | line:%(lineno)d] | %(module)s: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
            'level': 'DEBUG'
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'level': "WARNING",
            'formatter': 'detailed'
        },
        'file': {
            'class': "logging.handlers.RotatingFileHandler",
            'level': "WARNING",
            'formatter': 'detailed',
            'filename': f'{logging_path}/kameleon-error.log',
            "maxBytes": 1000000,
            "backupCount": 3
        },
    },
    "loggers": {
        'root': {
            'level': 'DEBUG',
            'handlers': ['stdout', 'stderr', 'file']
        }
    }
}


def setup_logging():
    pssh_logger = logging.getLogger("pssh")
    pssh_logger.setLevel(logging.CRITICAL)
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.DEBUG)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    dictConfig(config=logging_config)
