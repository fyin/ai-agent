import logging
import os
from typing import Optional

def configure_logging(log_file: Optional[str]=None, module_name:Optional[str]=None, log_level=logging.INFO) -> logging.Logger:
    """
    Configure project-level logging with console and file handlers.

    Args:
        log_file (str): Path to the log file.
        module_name (str): Name of the module for logging.
        log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: Configured logger for the project.
    """
    # Create a named logger for the project
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)

    # Prevent duplicate logs by clearing existing handlers
    logger.handlers.clear()

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # File handler
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger