import logging
from logging.config import dictConfig
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class LogColors:
    DEBUG: str = "\033[94m"  # Blue
    INFO: str = "\033[92m"  # Green
    WARNING: str = "\033[93m"  # Yellow
    ERROR: str = "\033[91m"  # Red
    CRITICAL: str = "\033[95m"  # Purple
    RESET: str = "\033[0m"
    TIME: str = "\033[96m"  # Cyan
    MODULE: str = "\033[97m"  # White


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt, datefmt)
        self.colors = LogColors()

    def format(self, record) -> str:
        color = getattr(self.colors, record.levelname, self.colors.RESET)
        log_fmt = (
            f"{self.colors.TIME}[%(asctime)s] {color}%(levelname)s{self.colors.RESET} "
            f"in {self.colors.MODULE}%(module)s [%(filename)s: %(lineno)d - %(funcName)s()]{self.colors.RESET}: "
            f"{color}%(message)s{self.colors.RESET}"
        )
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def create_logging_config() -> Dict:
    """Create a standardized logging configuration."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s] [%(filename)s: %(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "level": "DEBUG",
                "filename": "app.log",
                "mode": "a",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},
    }


def setup_logging() -> None:
    """Set up logging with colored console output."""
    dictConfig(create_logging_config())

    logger = logging.getLogger()
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setFormatter(ColoredFormatter())


# Automatically set up logging when module is imported
setup_logging()

if __name__ == "__main__":
    logging.debug("This is a debug message.")
    logging.info("This is an informational message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
