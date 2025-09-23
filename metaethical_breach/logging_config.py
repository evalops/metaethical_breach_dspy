"""
Logging configuration for the Metaethical Breach framework.

This module provides centralized logging configuration with different
levels for development and production use.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_style: str = "production"
) -> None:
    """Configure logging for the metaethical breach framework.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        format_style: Either 'development' or 'production'
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Choose format based on style
    if format_style == "development":
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s:%(lineno)d | %(levelname)s | %(message)s",
            datefmt="%H:%M:%S"
        )
    else:  # production
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configure specific loggers
    # Suppress overly verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Framework loggers
    framework_loggers = [
        "metaethical_breach.config",
        "metaethical_breach.data",
        "metaethical_breach.judge",
        "metaethical_breach.metrics",
        "metaethical_breach.evaluation",
        "metaethical_breach.experiment"
    ]

    for logger_name in framework_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))


def get_logger(name: str) -> logging.Logger:
    """Get a logger with consistent configuration.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class ExperimentLogger:
    """Context manager for experiment-specific logging."""

    def __init__(
        self,
        experiment_name: str,
        log_dir: str = "logs",
        level: str = "INFO"
    ):
        self.experiment_name = experiment_name
        self.log_dir = Path(log_dir)
        self.level = level
        self.log_file = self.log_dir / f"{experiment_name}.log"
        self.original_handlers = []

    def __enter__(self):
        """Set up experiment-specific logging."""
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging with experiment-specific file
        setup_logging(
            level=self.level,
            log_file=str(self.log_file),
            format_style="production"
        )

        logger = get_logger(__name__)
        logger.info("=" * 60)
        logger.info(f"Starting experiment: {self.experiment_name}")
        logger.info(f"Log file: {self.log_file}")
        logger.info("=" * 60)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up experiment logging."""
        logger = get_logger(__name__)

        if exc_type is not None:
            logger.error(f"Experiment failed: {exc_type.__name__}: {exc_val}")
        else:
            logger.info("Experiment completed successfully")

        logger.info("=" * 60)


def log_function_call(func):
    """Decorator to log function calls with arguments and results."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = f"{func.__module__}.{func.__name__}"

        # Log function entry
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func_name} failed: {type(e).__name__}: {e}")
            raise

    return wrapper


def log_api_call(model_name: str, request_type: str, success: bool, duration: float, error: Optional[str] = None):
    """Log API calls for monitoring and debugging.

    Args:
        model_name: Name of the model being called
        request_type: Type of request (e.g., 'generation', 'judgment')
        success: Whether the call succeeded
        duration: Duration in seconds
        error: Error message if failed
    """
    logger = get_logger("metaethical_breach.api")

    status = "SUCCESS" if success else "FAILED"
    log_msg = f"API_CALL | {model_name} | {request_type} | {status} | {duration:.3f}s"

    if success:
        logger.info(log_msg)
    else:
        logger.error(f"{log_msg} | ERROR: {error}")


# Default logging setup from environment
def setup_default_logging():
    """Set up default logging based on environment variables."""
    level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", None)
    format_style = os.getenv("LOG_FORMAT", "production")

    setup_logging(level=level, log_file=log_file, format_style=format_style)


# Auto-setup if imported
if not logging.getLogger().handlers:
    setup_default_logging()