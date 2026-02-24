"""Queue-based logging setup for non-blocking async log output.

Configures a ``QueueHandler`` / ``QueueListener`` pair so that all log
records are enqueued by the caller and consumed on a background thread,
keeping the main thread free of I/O overhead.
"""

import atexit
import logging
from logging.config import dictConfig
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Any


def setup_queue_logging(log_config: dict[str, Any], logger_name: str) -> tuple[QueueHandler, QueueListener]:
    """Set up queue-based logging using the provided logging configuration.

    Applies *log_config* via ``dictConfig``, extracts the resulting handlers,
    wraps them in a ``QueueListener``, and returns a ``QueueHandler`` that
    the caller should attach to the target logger.

    The listener is started immediately and registered for graceful shutdown
    via ``atexit``.

    Args:
        log_config: A ``logging.config.dictConfig``-compatible dictionary.
        logger_name: Name of the logger whose handlers should be migrated
            to the queue listener.

    Returns:
        A tuple of (``QueueHandler``, ``QueueListener``).
    """
    log_queue: Queue[Any] = Queue(-1)  # No limit on size

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
