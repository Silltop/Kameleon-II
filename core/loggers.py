import logging
import re


class ColorFormatter(logging.Formatter):
    cyan = "\x1b[36;20m"  # Cyan for DEBUG
    green = "\x1b[32;20m"  # Green for INFO
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    COLORS = {
        logging.DEBUG: cyan,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno)
        message = super().format(record)  # Use the existing format set in the logger
        return f"{color}{message}{self.reset}"


class FilterOutDateFromWerkzeugLog(logging.Filter):
    pattern: re.Pattern = re.compile(r' - - \[.+?] "')

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.pattern.sub(' - "', record.msg)
        return True
