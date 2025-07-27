import jsonlines

def read_data(input_path : str) -> list[dict]:
    result = []
    with jsonlines.open(input_path) as reader:
        for entry in reader:
            result.append(entry)
    return result

def save_data(data : list[dict], output_path : str) -> None:
    with jsonlines.open(output_path, mode="w") as writer:
        for line in data:
            writer.write(line)

from constants import ALTERNATE_DOMAINS, ALTERNATE_PROTOCOLS

def extract_article_name(url : str):
    name = None
    for protocol in ALTERNATE_PROTOCOLS:
        if url.startswith(protocol):
            url = url[len(protocol):]
            break
    for base in ALTERNATE_DOMAINS:
        if url.startswith(base):
            name = url[len(base):]
            break
    if name is None: raise ValueError(f"The url {url} does not conform to a known format.")
    return name

import logging
import sys

def get_logger(name : str, filename : str) -> logging.Logger:
    logger = logging.getLogger(name)
   
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