import sys
import threading
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger as _logger

_logger_instance = None
_logger_lock = threading.Lock()


def load_log_settings(settings_path: Optional[str] = None) -> dict:
    """Load logging settings from YAML file."""
    if settings_path is None:
        # Default path relative to this file
        settings_path = (
            Path(__file__).parent.parent.parent / "config" / "log_settings.yaml"
        )

    settings_path = Path(settings_path)
    if not settings_path.exists():
        # Return default settings if file doesn't exist
        return {
            "level": "INFO",
            "log_file": None,
            "rotation": "10 MB",
            "retention": "1 week",
            "encoding": "utf-8",
        }

    try:
        with settings_path.open("r", encoding="utf-8") as f:
            settings = yaml.safe_load(f) or {}
    except ImportError:
        # Fallback if yaml is not available
        settings = {}
    except Exception:
        settings = {}

    # Merge with defaults
    defaults = {
        "level": "INFO",
        "log_file": None,
        "rotation": "10 MB",
        "retention": "1 week",
        "encoding": "utf-8",
    }
    defaults.update(settings)
    return defaults


def define_log_level(
    print_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    encoding: str = "utf-8",
):
    """Adjust the log level to the specified level and optionally add file logging."""
    _logger.remove()

    # Console logging with colored output
    _logger.add(
        sys.stderr,
        level=print_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{function}:{line}</cyan> | <level>{message}</level>",
        colorize=True,
    )

    # File logging if specified (no colors for file)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        _logger.add(
            log_path,
            level=print_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            rotation=rotation,
            retention=retention,
            encoding=encoding,
            colorize=False,  # No colors in log files
        )

    return _logger


def configure_logger(
    print_level: Optional[str] = None,
    log_file: Optional[str] = None,
    settings_path: Optional[str] = None,
):
    """Configure logger with level and optional file output."""
    global _logger_instance
    with _logger_lock:
        if print_level is None or log_file is None:
            settings = load_log_settings(settings_path)
            print_level = print_level or settings["level"]
            log_file = log_file or settings["log_file"]

        _logger_instance = define_log_level(
            print_level=print_level,
            log_file=log_file,
            rotation=settings.get("rotation", "10 MB"),
            retention=settings.get("retention", "1 week"),
            encoding=settings.get("encoding", "utf-8"),
        )
        return _logger_instance


def get_logger():
    global _logger_instance
    if _logger_instance is None:
        with _logger_lock:
            if _logger_instance is None:
                # Load from default settings
                settings = load_log_settings()
                _logger_instance = define_log_level(
                    print_level=settings["level"],
                    log_file=settings["log_file"],
                    rotation=settings["rotation"],
                    retention=settings["retention"],
                    encoding=settings["encoding"],
                )
    return _logger_instance


def reset_logger():
    global _logger_instance
    with _logger_lock:
        _logger_instance = None


class _LazyLoggerProxy:
    """Lazy proxy for logger to support dynamic configuration."""

    def __getattr__(self, name):
        return getattr(get_logger(), name)

    def __repr__(self):
        return repr(get_logger())


logger = _LazyLoggerProxy()


# Utility functions for common logging patterns
def log_function_call(func_name: str, args: dict = None, level: str = "DEBUG"):
    """Log function entry with arguments."""
    args_str = f" with args: {args}" if args else ""
    getattr(logger, level.lower())(f"Calling {func_name}{args_str}")


def log_performance(func_name: str, duration: float, level: str = "INFO"):
    """Log function performance."""
    getattr(logger, level.lower())(f"{func_name} completed in {duration:.4f}s")


def log_error_with_context(error: Exception, context: str = "", level: str = "ERROR"):
    """Log error with additional context."""
    getattr(logger, level.lower())(f"{context}: {str(error)}")


if __name__ == "__main__":
    # Configure logger from settings file
    configure_logger()

    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    # Test utility functions
    log_function_call("test_function", {"param1": "value1"})
    log_performance("test_function", 0.1234)

    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error_with_context(e, "Test context")
        logger.exception(f"An error occurred: {e}")
