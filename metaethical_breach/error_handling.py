"""
Error handling utilities for the Metaethical Breach framework.

This module provides consistent error handling patterns, custom exceptions,
and retry logic for robust production operation.
"""

from __future__ import annotations

import time
import functools
from typing import Type, Union, Callable, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class MetaethicalBreachError(Exception):
    """Base exception for metaethical breach framework errors."""
    pass


class ConfigurationError(MetaethicalBreachError):
    """Raised when configuration is invalid or missing."""
    pass


class ModelAPIError(MetaethicalBreachError):
    """Raised when model API calls fail."""

    def __init__(self, message: str, model_name: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.model_name = model_name
        self.original_error = original_error


class JudgeVulnerabilityError(MetaethicalBreachError):
    """Raised when judge model is too vulnerable for reliable evaluation."""

    def __init__(self, message: str, vulnerability_score: float):
        super().__init__(message)
        self.vulnerability_score = vulnerability_score


class SampleSizeError(MetaethicalBreachError):
    """Raised when sample size is inadequate for reliable analysis."""

    def __init__(self, message: str, current_n: int, required_n: int):
        super().__init__(message)
        self.current_n = current_n
        self.required_n = required_n


class ExperimentFailureError(MetaethicalBreachError):
    """Raised when experiment fails in a way that makes results invalid."""
    pass


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_backoff: bool = True
    jitter: bool = True


def with_retry(
    exceptions: Union[Type[Exception], tuple] = Exception,
    config: Optional[RetryConfig] = None
) -> Callable:
    """Decorator to add retry logic to functions.

    Args:
        exceptions: Exception types to retry on
        config: Retry configuration

    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts")
                        raise

                    # Calculate delay
                    if config.exponential_backoff:
                        delay = min(config.base_delay * (2 ** attempt), config.max_delay)
                    else:
                        delay = config.base_delay

                    if config.jitter:
                        import random
                        delay *= (0.5 + random.random())  # Add 50-100% jitter

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}): "
                        f"{type(e).__name__}: {e}. Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

            # This should never be reached due to the raise above
            raise last_exception

        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    log_errors: bool = True,
    **kwargs
) -> Any:
    """Safely execute a function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default_return: Value to return if function fails
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default_return if failed
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Safe execution of {func.__name__} failed: {type(e).__name__}: {e}")
        return default_return


def validate_config(config: Any, required_fields: List[str]) -> None:
    """Validate that configuration has required fields.

    Args:
        config: Configuration object to validate
        required_fields: List of required field names

    Raises:
        ConfigurationError: If required fields are missing
    """
    missing_fields = []

    for field in required_fields:
        if not hasattr(config, field) or getattr(config, field) is None:
            missing_fields.append(field)

    if missing_fields:
        raise ConfigurationError(
            f"Missing required configuration fields: {', '.join(missing_fields)}"
        )


def validate_sample_size(current_n: int, required_n: int, min_acceptable_power: float = 0.5) -> None:
    """Validate that sample size is adequate for analysis.

    Args:
        current_n: Current sample size
        required_n: Required sample size for adequate power
        min_acceptable_power: Minimum acceptable power level

    Raises:
        SampleSizeError: If sample size is too small
    """
    from .metrics import calculate_power

    current_power = calculate_power(current_n, effect_size=0.1)

    if current_power < min_acceptable_power:
        raise SampleSizeError(
            f"Sample size {current_n} is too small (power={current_power:.3f}, "
            f"required power>={min_acceptable_power}). Need at least {required_n} samples.",
            current_n=current_n,
            required_n=required_n
        )


def validate_judge_robustness(vulnerability_score: float, max_acceptable: float = 0.1) -> None:
    """Validate that judge model is robust enough for evaluation.

    Args:
        vulnerability_score: Judge vulnerability score (0-1)
        max_acceptable: Maximum acceptable vulnerability

    Raises:
        JudgeVulnerabilityError: If judge is too vulnerable
    """
    if vulnerability_score > max_acceptable:
        raise JudgeVulnerabilityError(
            f"Judge model is too vulnerable (score={vulnerability_score:.3f}, "
            f"max acceptable={max_acceptable}). Results may be unreliable.",
            vulnerability_score=vulnerability_score
        )


class ErrorContext:
    """Context manager for enhanced error reporting."""

    def __init__(self, operation: str, critical: bool = False):
        self.operation = operation
        self.critical = critical
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else 0

        if exc_type is None:
            logger.debug(f"Operation completed: {self.operation} ({duration:.3f}s)")
        else:
            error_msg = f"Operation failed: {self.operation} ({duration:.3f}s) - {exc_type.__name__}: {exc_val}"

            if self.critical:
                logger.critical(error_msg)
                # For critical operations, wrap in ExperimentFailureError
                if not isinstance(exc_val, MetaethicalBreachError):
                    raise ExperimentFailureError(f"Critical operation failed: {self.operation}") from exc_val
            else:
                logger.error(error_msg)

        return False  # Don't suppress exceptions


def handle_api_error(func: Callable) -> Callable:
    """Decorator to handle API-related errors consistently.

    This decorator catches common API errors and converts them to
    ModelAPIError with additional context.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Extract model name from args/kwargs if possible
            model_name = "unknown"
            if args and hasattr(args[0], 'model'):
                model_name = args[0].model
            elif 'model' in kwargs:
                model_name = kwargs['model']

            # Convert to ModelAPIError
            raise ModelAPIError(
                f"API call failed: {type(e).__name__}: {e}",
                model_name=model_name,
                original_error=e
            ) from e

    return wrapper


def graceful_shutdown(cleanup_funcs: List[Callable] = None) -> None:
    """Perform graceful shutdown with cleanup.

    Args:
        cleanup_funcs: List of cleanup functions to call
    """
    logger.info("Initiating graceful shutdown...")

    if cleanup_funcs:
        for cleanup_func in cleanup_funcs:
            try:
                cleanup_func()
                logger.debug(f"Cleanup function {cleanup_func.__name__} completed")
            except Exception as e:
                logger.error(f"Cleanup function {cleanup_func.__name__} failed: {e}")

    logger.info("Graceful shutdown completed")


# Global error handlers for common scenarios
def setup_global_error_handling():
    """Set up global error handling for the framework."""
    import sys

    def exception_handler(exc_type, exc_value, exc_traceback):
        """Global exception handler."""
        if issubclass(exc_type, KeyboardInterrupt):
            logger.info("Experiment interrupted by user")
            graceful_shutdown()
            return

        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = exception_handler