import atexit
import logging
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Any


def setup_queue_logging(log_config: dict[str, Any], logger_name: str):
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
