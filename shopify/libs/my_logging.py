import logging
import sys


def getLogger(name: str = None) -> logging.Logger:
    # create logger with 'name'
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    precise_formatter = logging.Formatter(
        '%(asctime)s;%(name)-15s;%(levelname)-8s;%(message)s'
    )
    console_handler.setFormatter(precise_formatter)
    # add the handlers to the logger
    logger.addHandler(console_handler)
    return logger
