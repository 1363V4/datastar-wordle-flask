import logging
from .paths import *


logger = logging.getLogger('legovh')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(PATH_LOG / "perso.log")

file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
