from constants import ALTERNATE_BASE_URLS

def extract_article_name(url : str):
    name = None
    for base in ALTERNATE_BASE_URLS:
        if url.startswith(base):
            name = url[len(base):]
            break
    if name is None: raise ValueError(f"The url {url} does not conform to a known format.")
    return name

import logging
import sys

def get_logger(filename : str) -> logging.Logger:
    logger = logging.getLogger(__name__)
   
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)

    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

    fileHandler = logging.FileHandler(filename, encoding="utf-8")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger