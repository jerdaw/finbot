import logging
from pathlib import Path

from config.logger_config import get_logger_config
from constants.path_constants import LOGS_DIR
from libs.logger.setup_queue_logging import setup_queue_logging


def initialize_logger(logger_name: str, log_level: str, log_dir: Path = LOGS_DIR) -> logging.Logger:
    """
    Initialize the logger for the application.
    """

    if not log_dir.exists():
        raise ValueError(f"Log directory for {logger_name} does not exist: {log_dir}")

    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        log_config = get_logger_config(logger_name=logger_name, log_level=log_level, log_dir=log_dir)

        # Start the queue listener
        queue_handler, _ = setup_queue_logging(log_config=log_config, logger_name=logger_name)

        # Add the QueueHandler to the logger
        logger.setLevel(log_level)
        logger.addHandler(queue_handler)

    return logger


# Note: Do not actually initialize the logging configuration here. Use the environment configs instead.
if __name__ == "__main__":
    from config import logger

    logger.debug("Test debug message.")  # May not show if DEBUG is not enabled in the environment config
    logger.info("Test log message.", extra={"extra_key": "extra_val"})  # extra will show up in the jsonl file
    logger.warning("Test warning message.")
    logger.error("Test error message.")
    logger.critical("Test critical message.")
