from loguru import logger
from utils.sleep import sleep
from settings import RETRY_COUNT

def retry(func):
    def wrapper(*args, **kwargs):
        retries = 1
        while retries <= RETRY_COUNT:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{e}")
                if RETRY_COUNT > 1: sleep(5, 10)
                retries += 1
        logger.critical('Превышено количество попыток!')
        exit()
    return wrapper
