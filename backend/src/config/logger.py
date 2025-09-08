import logging
import sys


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s][%(filename)s].%(funcName)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        # logging.StreamHandler(sys.stdout),
        logging.FileHandler("server.log", encoding='utf-8')
    ],
)

def get_logger(name:str) -> logging.Logger:
    return logging.getLogger(name)