import logging

def get_logger(file):
    LOGGING_LEVEL = 'INFO'
    LOGGING_FORMAT = '[%(asctime)s] %(name)s:%(lineno)d: %(message)s'
    logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
    logger = logging.getLogger(file)
    return logger
