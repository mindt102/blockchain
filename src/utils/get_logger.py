import logging


def get_logger(logger_name:str) -> logging.Logger:
    """
    Take in a logger_name and generate a logger with the follow properties:
    - Formatter of format [%(asctime)s] - [%(levelname)s] - [%(message)s] - [%(name)s]
    - Log info level to a central LOG_FILE
    - Log warning level to stream
    :return logger: An object of type Logger with the name of logger_name
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(f"[%(asctime)s] - [%(levelname)s] - [%(message)s] - [%(name)s]")
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    return logger
