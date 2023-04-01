"""Set logger for entire application."""

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logging_handler = logging.StreamHandler()
logging_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '[%(levelname)s]:%(asctime)s - %(filename)s - %(funcName)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)
logging_handler.setFormatter(formatter)

logger.addHandler(logging_handler)
