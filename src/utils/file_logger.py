"""File logging utilities."""

import logging
from datetime import datetime
from pathlib import Path


def setup_file_logger(log_file: str = "generation.log") -> logging.Logger:
    """Set up a file logger for debugging."""
    # Create logger
    logger = logging.getLogger("news_generator")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers = []

    # Create file handler
    fh = logging.FileHandler(log_file, mode="w")
    fh.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(formatter)

    # Add handler
    logger.addHandler(fh)

    logger.info("=" * 80)
    logger.info(f"News generation started at {datetime.now()}")
    logger.info("=" * 80)

    return logger


def get_logger() -> logging.Logger:
    """Get the file logger instance."""
    return logging.getLogger("news_generator")
