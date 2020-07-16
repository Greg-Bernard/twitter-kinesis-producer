import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def configure_logger(
    name='sender',
    to_stdout=False, # Whether to log to stdout or not
    folder='logs'
):
    """
    Configure the default logger behaviour for this project.
    """
    # Create a logging directory
    folder_path = Path(folder)
    os.makedirs(exist_ok=True, name=folder)

    # Configure logger
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%Y-%M-%D %H:%M:%S'
    )

    # Logger to rotate the log file every 10MBs and keep 1 backup of previous log file.
    filename = name + '.log'
    handler = RotatingFileHandler(
        folder_path / filename, 
        mode='a', 
        maxBytes=10 * 1000 * 1024,
        backupCount=10
    )
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')                            
    handler.setFormatter(formatter)

    # Create logger
    logger = logging.getLogger(name)
    logger.propagate = to_stdout
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger