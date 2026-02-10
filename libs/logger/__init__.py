import logging

from config.project_config import settings
from libs.logger.initialize_logger import initialize_logger

# Initialize logger
logger: logging.Logger = initialize_logger(
    logger_name=settings.get("name", "finbot"),
    log_level=settings.get("logging.level", "INFO"),
)
