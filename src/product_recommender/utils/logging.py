"""Logging utilities for the Product Recommender project.

Provides a configurable logger setup for both console and file output,
with support for rotating log files and custom log levels.

Usage:
    logger = get_logger(__name__)

Reference:
    https://docs.python.org/3/howto/logging.html#configuring-logging
"""

import logging
import logging.handlers
import sys
from pathlib import Path


def get_logger(
    name: str,
    log_in_console: bool = True,
    log_in_file: bool = True,
    log_file_path: Path | None = None,
    console_log_level: int = logging.INFO,
    file_log_level: int = logging.DEBUG,
) -> logging.Logger:
    """Creates and returns a logger configured as per parameters.

    Reference: https://docs.python.org/3/howto/logging.html#configuring-logging
    Sets the root logger to WARNING level
    and creates a new logger with the given name with propagate set to False.
    All downstream loggers inherit the configuration.
    Ex: get_logger("xyz.abc") inherits the configuration of get_logger("xyz").

    Args:
      name: logger name (use __name__ in scripts)
      log_in_console: enable console logging
      log_in_file: enable file logging
      log_file_path: path to store log file
      console_log_level: your app logger level (default INFO)
      file_log_level: your app logger level (default INFO)

    Returns:
      Configured logger instance.
    """
    # Set up root logger to suppress dependency noise
    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    # Clear any existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Create app logger
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent duplication via root

    # Set logger level to the minimum of handler levels
    # to allow messages to pass through
    logger.setLevel(min(console_log_level, file_log_level))

    log_format = (
        "[%(asctime)s [%(levelname)s] %(funcName)s] "
        "[%(pathname)s:%(lineno)d]: %(message)s"
    )
    formatter = logging.Formatter(log_format)

    # Console handler
    if log_in_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(formatter)
        root.addHandler(console_handler)
        logger.addHandler(console_handler)

    # File handler
    if log_in_file:
        if log_file_path is None:
            log_file_path = Path(__file__).parents[3] / ".logs" / f"{name}.log"
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        logger.addHandler(file_handler)
    return logger
