# streamsim/src/core/logger.py

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: str = "streamsim.log",
    console: bool = False,
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt: str = '%Y-%m-%d %H:%M:%S'
) -> None:
    """
    Configure root logging for the entire application.
    Call this ONCE at application startup.

    Args:
        level: Logging level
        log_file: Path to log file
        console: If True, also output to stdout
        log_format: Custom format string
        datefmt: Date format string
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    formatter = logging.Formatter(log_format, datefmt=datefmt)

    # File handler
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (optional)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger that inherits the root configuration.
    No per-logger setup needed — just call this and it works.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)