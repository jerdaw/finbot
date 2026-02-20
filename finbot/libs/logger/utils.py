import datetime
import json
import logging
from typing import Any


class ColorFormatter(logging.Formatter):
    """
    Custom formatter for colorized output.
    """

    COLORS = {  # noqa: RUF012 - Class attribute intentionally not ClassVar for formatter pattern
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[0;41m",  # Red background
    }

    def format(self, record: logging.LogRecord) -> str:
        indent_aligner = " " * (1 + max(len(k) for k in self.COLORS) - len(record.levelname))
        base_fmt = getattr(self, "_fmt", "")
        log_fmt = base_fmt + "%(levelname)s]" + indent_aligner + "%(message)s\033[0m"
        formatter = logging.Formatter(log_fmt)
        if record.levelname in self.COLORS:
            log_fmt = self.COLORS[record.levelname] + log_fmt
            formatter = logging.Formatter(log_fmt, self.datefmt)
        return formatter.format(record)


class LoggingJsonFormatter(logging.Formatter):
    def __init__(
        self,
        *args: Any,
        rename_fields: dict[str, str] | None = None,
        static_fields: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.rename_fields = rename_fields or {}
        self.static_fields = static_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        message = self.create_log_record(record)
        return json.dumps(message, default=self.json_default)

    def create_log_record(self, record: logging.LogRecord) -> dict[str, Any]:
        # Standard fields
        log_record = {
            "timestamp": datetime.datetime.fromtimestamp(record.created, datetime.UTC).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Static fields
        log_record.update(self.static_fields)

        # Custom field renaming
        for old_key, new_key in self.rename_fields.items():
            if old_key in log_record:
                log_record[new_key] = log_record.pop(old_key)

        # Include exception info
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Include stack info
        if record.stack_info:
            log_record["stack_info"] = record.stack_info

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_record and not key.startswith("_"):
                log_record[key] = value

        return log_record

    def json_default(self, obj: Any) -> str:
        if isinstance(obj, datetime.date | datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, Exception):
            return str(obj)
        return str(obj)  # Default for other types


class NonErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.WARNING  # Pass logs of WARNING and below


class ErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR  # Pass logs of ERROR and above
