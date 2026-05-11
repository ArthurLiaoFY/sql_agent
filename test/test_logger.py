#!/usr/bin/env python3
"""
Test script for the unified logging configuration.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.logger.logger import (
    configure_logger,
    log_function_call,
    log_performance,
    logger,
    load_log_settings
)


def main():
    # Configure logger from settings file
    configure_logger()

    logger.info("Logger configuration test started")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")

    # Test utility functions
    log_function_call("test_function", {"param": "value"})
    log_performance("test_function", 0.567)

    try:
        # Simulate an error
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.error(f"Caught an error: {e}")
        logger.exception("Full exception details")

    logger.info("Logger configuration test completed")


if __name__ == "__main__":
    print(load_log_settings())
