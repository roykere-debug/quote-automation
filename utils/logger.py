import logging
import sys
from pathlib import Path


def setup_logger(name: str = "quote_automation") -> logging.Logger:
    """Set up centralized logger with file and console handlers"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:  # Prevent duplicate handlers
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler - full detail
    file_handler = logging.FileHandler(
        log_dir / "quote_automation.log",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Console handler - INFO and above only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
