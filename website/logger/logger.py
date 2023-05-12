import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.ERROR)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('website/logger/logfile.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)