"""Logging configuration for the literator package."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from rich.logging import RichHandler
from rich.console import Console
import appdirs

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_DEBUG_LOG_LEVEL = logging.DEBUG


def get_log_dir() -> Path:
    """
    Get the appropriate directory for storing log files.
    Uses appdirs to get the system's appropriate log directory.
    """
    app_name = "literator"
    app_author = "literator"

    # Use appdirs to get system's standard log directory
    log_dir = Path(appdirs.user_log_dir(app_name, app_author))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    debug: bool = False,
    log_file: Optional[Union[str, Path]] = None,
    log_to_file: bool = True,
    log_to_console: bool = True,
    logger_name: str = "literator",
) -> logging.Logger:
    """
    Set up logging for the application with Rich formatting for console
    and file logging for persistence.

    Args:
        debug: Whether to enable debug logging level
        log_file: Optional specific log file path. If None, a default is used
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        logger_name: Name for the logger

    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger(logger_name)

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Determine log level based on debug flag
    console_level = DEFAULT_DEBUG_LOG_LEVEL if debug else DEFAULT_LOG_LEVEL
    file_level = DEFAULT_DEBUG_LOG_LEVEL  # Always log debug to file

    # Set the overall logger level to the most verbose needed
    logger.setLevel(min(console_level, file_level))

    handlers = []

    # Configure console handler with Rich formatting
    if log_to_console:
        console = Console()
        rich_handler = RichHandler(
            level=console_level,
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=debug,
            show_time=True,
            show_path=debug,
        )
        rich_handler.setFormatter(logging.Formatter("%(message)s"))
        handlers.append(rich_handler)

    # Configure file handler if requested
    if log_to_file:
        if log_file is None:
            # Generate default log file path in system log directory
            timestamp = datetime.now().strftime("%Y%m%d")
            log_dir = get_log_dir()
            log_file = log_dir / f"{logger_name}_{timestamp}.log"

        # Convert str to Path if needed
        if isinstance(log_file, str):
            log_file = Path(log_file)

        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(file_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Add all handlers to logger
    for handler in handlers:
        logger.addHandler(handler)

    # Log setup information
    logger.debug(f"Logger initialized: debug={debug}")
    if log_to_file:
        logger.debug(f"Logging to file: {log_file}")

    return logger


def get_logger(name: str = "literator") -> logging.Logger:
    """
    Get a configured logger. If the logger has not been set up yet,
    this will return the default logger.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
