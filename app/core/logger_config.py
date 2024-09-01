import logging
import os

import logstash

LOGSTASH_HOST = os.getenv("LOGSTASH_HOST")
LOGSTASH_PORT = os.getenv("LOGSTASH_PORT")


def setup_logger(name: str = "app-logstash") -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    logstash_handler = logstash.TCPLogstashHandler(LOGSTASH_HOST, LOGSTASH_PORT, version=1)
    logger.addHandler(logstash_handler)

    console_handler = logging.StreamHandler()
    # console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    return logger
