import logging

from finbot.config.project_config import settings
from finbot.libs.logger.audit import (
    audit_operation,
    emit_audit_event,
    generate_trace_id,
    get_trace_id,
    set_trace_id,
)
from finbot.libs.logger.initialize_logger import initialize_logger

# Initialize logger
logger: logging.Logger = initialize_logger(
    logger_name=settings.get("name", "finbot"),
    log_level=settings.get("logging.level", "INFO"),
)

__all__ = [
    "audit_operation",
    "emit_audit_event",
    "generate_trace_id",
    "get_trace_id",
    "logger",
    "set_trace_id",
]
