import logging
from colorlog import ColoredFormatter
import os


def getLogger(name):
    return logging.getLogger(__name__)


def initialize_logger(output_dir, debug, level=False):
    NOTE = 15
    COLOR_FORMAT = "%(log_color)s%(levelname)s-%(name)s(%(lineno)d)%(reset)s: %(message)s"
    COLOR_FORMAT_INFO = "%(log_color)s%(levelname)s%(reset)s: %(message)s"
    FORMAT = "%(levelname)s-%(name)s(%(lineno)d): %(message)s"
    FORMAT_INFO = "%(levelname)s %(message)s"
    logging.addLevelName(NOTE, "NOTE")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_dir = os.path.join(output_dir, "log")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    def note(self, message, *args, **kws):
        self.log(NOTE, message, *args, **kws)

    logging.Logger.note = note
    numeric_level = getattr(logging, "DEBUG", None)
    if not debug:
        numeric_level = getattr(logging, "INFO", None)
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    if level:
        handler.setLevel(logging.DEBUG)
    formatter = ColoredFormatter(COLOR_FORMAT_INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), "w", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = ColoredFormatter(COLOR_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "run.log"), "w")
    handler.setLevel(numeric_level)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "trace.log"),"w")
    handler.setLevel(NOTE)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
