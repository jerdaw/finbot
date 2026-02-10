from __future__ import annotations

from pathlib import Path
from typing import Any

from libs.logger.utils import ColorFormatter, ErrorFilter, LoggingJsonFormatter, NonErrorFilter


def get_logger_config(logger_name: str, log_level: str, log_dir: Path) -> dict[str, Any]:
    """
    Prepare and get logging configuration based on given parameters.

    Args:
        logger_name (str): The name of the logger.
        log_level (str): The log level to be set for the logger.
        log_dir (Path): The directory where the logs will be stored.

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
            "non_error_filter": {
                "()": NonErrorFilter,
            },
            "error_filter": {
                "()": ErrorFilter,
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored",  # Store ephemeral logs in an easily readable format
                "filters": ["non_error_filter"],
                "stream": "ext://sys.stdout",
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "colored",  # Store ephemeral logs in an easily readable format
                "filters": ["error_filter"],
                "stream": "ext://sys.stderr",
            },
            # Smaller log that matches the console output for easy viewing
            "file_output": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "colored",
                "filename": str(log_dir / f"{logger_name}.log"),
                "maxBytes": 1024 * 1024 * 2,  # 2 MB
                "backupCount": 3,
            },
            # Full log in jsonl (json lines) format for easy parsing later
            "file_jsonl": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": str(log_dir / f"{logger_name}.log.jsonl"),
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 3,
            },
        },
        "loggers": {
            logger_name: {
                "handlers": ["stdout", "stderr", "file_output", "file_jsonl"],
                "level": log_level,
                "propagate": True,
            },
        },
    }
