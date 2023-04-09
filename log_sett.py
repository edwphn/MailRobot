"""
log_settings.py

This module provides a pre-configured logger for use in other Python files.
The logger has the following configurations:

1. General log configuration:
    - Logs messages with level DEBUG and above.
    - Logs messages to the console and 'main.log' file.
    - Excludes messages with 'emails' tag from console output.

2. Report log configuration:
    - Logs messages with level DEBUG and above.
    - Logs messages to the console and 'report.log' file.
    - Includes only messages with 'report' tag for console output.
    - Logs only message content in 'report.log' file.

Import the logger object from this module to use the configured logger.
"""

from loguru import logger
import sys


report_log = 'report.log'

def contextualize_class_logs(tag):
    def class_decorator(cls):
        class Wrapped(cls):
            def __getattribute__(self, name):
                attr = super().__getattribute__(name)
                if callable(attr):
                    def wrapped(*args, **kwargs):
                        with logger.contextualize(tag=tag):
                            return attr(*args, **kwargs)
                    return wrapped
                return attr
        return Wrapped
    return class_decorator


def configure_logger() -> None:
    logger.remove()

    format_string = ("<green>{time:DD-MM-YYYY HH:mm:ss}</green> | "
                     "<level>{level: <8}</level> | <cyan>{name}</cyan> | "
                     "<blue>{function}:{line}</blue> | {message}")

    # General log configuration
    logger.add("main.log", level="DEBUG", format=format_string, enqueue=True,
               backtrace=True, diagnose=True, rotation="5 MB")

    # Colorize console messages
    console_format_string = ("<green>{time:DD-MM-YYYY HH:mm:ss}</green> | "
                             "<level>{level: <8}</level> | <cyan>{name}</cyan> | "
                             "<blue>{function}:{line}</blue> | <yellow>{message}</yellow>")
    logger.add(sys.stdout, level="DEBUG",
               format=console_format_string, enqueue=True, backtrace=True, diagnose=True,
               filter=lambda record: record["extra"].get("tag") != "emails")

    # Report log configuration
    report_format_string = "{message}"
    logger.add(report_log, level="DEBUG", format=report_format_string,
               enqueue=True, backtrace=True, diagnose=True,
               filter=lambda record: record["extra"].get("tag") == "report")


configure_logger()