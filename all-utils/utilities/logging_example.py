import logging 
import sys

def get_app_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler("utility_logging_example.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger



def run_logging_demo() ->None:
    logger = get_app_logger("utility_logger")

    logger.debug("Debugging values: %s", {"step": 1, "status": "starting"})
    logger.info("Application example started.")
    logger.warning("This is a warning example for the logging utility.")

    try:
        value = 10 / 0
    except ZeroDivisionError:
        logger.exception("An exception occurred while dividing by zero.")
    
    logger.info("Logging demo finished.")