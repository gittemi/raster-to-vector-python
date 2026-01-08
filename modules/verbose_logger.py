import logging
from enum import Enum

# TODO (P3): Support TRACE level logging

class Verbosity(Enum):
    SILENT = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3

class _ColorFormatter(logging.Formatter):
    """
    Class to specify which colours to display each log level with.
    """
    COLORS = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[32m",     # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",    # Red
        logging.CRITICAL: "\033[1;31m"
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"
    
class VerboseLogger:
    def __init__(self,
                 verbosity: Verbosity = Verbosity.SILENT,
                 class_name: str = None):
        self.class_name = class_name

        logging_level = logging.WARNING
        if verbosity >= 2:
            logging_level = logging.DEBUG
        elif verbosity == 1:
            logging_level = logging.INFO

        handler = logging.StreamHandler()
        handler.setFormatter(_ColorFormatter(
            f"%(levelname)-8s | %(name)-15s \t| %(funcName)-25s \t| %(message)s"
        ))

        logger = logging.getLogger(self.class_name)
        logger.setLevel(logging_level)
        logger.addHandler(handler)
        self.logger = logger
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, stacklevel=2, **kwargs)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.earning(message)