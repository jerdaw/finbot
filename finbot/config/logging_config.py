from __future__ import annotations

import atexit
import logging
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from queue import Queue
from typing import Any

from finbot.constants.path_constants import LOGS_DIR
from finbot.libs.logger.utils import ColorFormatter, ErrorFilter, LoggingJsonFormatter, NonErrorFilter


def prepare_logging_config(logger_name: str, log_level: str, log_file_path: Path) -> dict[str, Any]:
    """
    Prepare logging configuration based on given parameters.

    Args:
        logger_name (str): The name of the logger.
        log_level (str): The log level to be set for the logger.
        log_file_path (Path | str): The file path where the log file will be created.

    Returns:
        dict: The logging configuration dictionary.

    """
    return {
        "version": 1,
        "disable_existing_loggers": False,  # Disable other loggers
        "formatters": {
            "colored": {"()": ColorFormatter, "format": "[%(asctime)s|%(name)s|", "datefmt": "%H:%M:%S"},
            "json": {
                "()": LoggingJsonFormatter,  # Use custom JSON formatter
            },
        },
        "filters": {
            "info_filter": {
                "()": NonErrorFilter,
            },
            "error_filter": {
                "()": ErrorFilter,
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "colored",  # Store ephemeral logs in an easily readable format
                "filters": ["info_filter"],
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "colored",  # Store ephemeral logs in an easily readable format
                "filters": ["error_filter"],
                "stream": "ext://sys.stderr",
            },
            "file_colored": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "colored",  # For easy viewing and persistence
                "filename": str(log_file_path.parent / f"{log_file_path.stem}-colored{log_file_path.suffix}"),
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 3,
            },
            "file_json": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",  # Store persistent logs in json format so they can be parsed later
                "filename": str(log_file_path.parent / f"{log_file_path.stem}-jsonl{log_file_path.suffix}.jsonl"),
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 3,
            },
        },
        "loggers": {
            logger_name: {
                "handlers": ["stdout", "stderr", "file_colored", "file_json"],
                "level": log_level,
                "propagate": True,
            },
        },
    }


def _setup_queue_logging(log_config: dict[str, Any], logger_name: str):
    """
    Set up queue logging using the provided logging configuration.
    """
    log_queue: Queue = Queue(-1)  # No limit on size

    # Apply the logging configuration
    dictConfig(log_config)

    # Retrieve the logger with its handlers
    configured_logger = logging.getLogger(logger_name)

    # Extract handlers for the QueueListener
    handlers = list(configured_logger.handlers)

    # Remove these handlers from the logger to prevent direct logging
    for handler in handlers:
        configured_logger.removeHandler(handler)

    # Create QueueHandler and QueueListener
    queue_handler = QueueHandler(log_queue)
    listener = QueueListener(log_queue, *handlers)
    listener.start()
    atexit.register(listener.stop)

    return queue_handler, listener


def initialize_logger(logger_name: str, log_level: str, log_dir: Path = LOGS_DIR) -> logging.Logger:
    """
    Initialize the logger for the application.
    """
    log_path = log_dir / f"{logger_name}.log"

    if not log_dir.exists():
        raise ValueError(f"Log directory for {logger_name} does not exist: {log_dir}")

    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        log_config = prepare_logging_config(logger_name, log_level, log_path)

        # Start the queue listener
        queue_handler, _ = _setup_queue_logging(log_config, logger_name)

        # Add the QueueHandler to the logger
        logger.setLevel(log_level)
        logger.addHandler(queue_handler)

    return logger


# Note: Do not actually initialize the logging configuration here. Use the environment configs instead.
if __name__ == "__main__":
    from finbot.config import logger

    logger.info("This is a test log message.")
    logger.info("This is a test log message.", extra={"test": "test"})  # The extra will show up in the jsonl fils
    logger.debug("This is a test debug message.")
    logger.warning("This is a test warning message.")
    logger.error("This is a test error message.")
    logger.critical("This is a test critical message.")
