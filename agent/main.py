import json
import os
from logging.config import dictConfig
import logging
from os import getcwd
from api import app
from werkzeug.exceptions import default_exceptions
import routes

logger = logging.getLogger("Kameleon-agent")
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
            'format': '[%(asctime)s | %(levelname)s] module:%(module)s: %(message)s ',
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


def _override_flask_exceptions():
    for exc in default_exceptions:
        app.register_error_handler(exc, _handle_flask_exception)


def _handle_flask_exception(exception_object):
    response = exception_object.get_response()
    http_error_code = exception_object.code
    if 400 <= http_error_code < 500:
        error_description = "This is a client error, make sure you provided correct data."
    elif 500 <= http_error_code < 600:
        error_description = "This is a server error, please provide this error to support team."
    else:
        error_description = "Unknown error"
    response_data = {
        "code": exception_object.code,
        "description": error_description,
        "error": exception_object.description,
    }
    response.data = json.dumps(response_data)  # Convert data to JSON string
    response.content_type = "application/json"  # Set content type
    logging.error(f"API returned error: {http_error_code}, with description: {exception_object.description}")
    return response

def setup_logging():
    dictConfig(config=logging_config)


if __name__ == "__main__":
    setup_logging()

    _override_flask_exceptions()
    app.run(host="0.0.0.0", debug=True, use_reloader=True, port=6622)
