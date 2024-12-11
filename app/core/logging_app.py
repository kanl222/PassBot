import logging
from logging.config import dictConfig

COLORS = {
    'DEBUG': '\033[94m',  # Синий
    'INFO': '\033[92m',  # Зеленый
    'WARNING': '\033[93m',  # Желтый
    'ERROR': '\033[91m',  # Красный
    'CRITICAL': '\033[95m'  # Пурпурный
}

class ColoredFormatter(logging.Formatter):

    RESET = '\033[0m'
    COLOR_TIME = '\033[96m'  # Голубой
    COLOR_MODULE = '\033[97m'  # Белый

    def format(self, record) -> str:
        color = COLORS.get(record.levelname, self.RESET)
        log_fmt = (
            f"{self.COLOR_TIME}[%(asctime)s] {color}%(levelname)s{self.RESET} "
            f"in {self.COLOR_MODULE}%(module)s [%(filename)s: %(lineno)d - %(funcName)s()]{self.RESET}: "
            f"{color}%(message)s{self.RESET}"
        )
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging() -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s] [%(filename)s: %(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
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
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        },
    }

    dictConfig(logging_config)

    logger = logging.getLogger()
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setFormatter(ColoredFormatter())


setup_logging()

if __name__ == '__main__':
    logging.debug("This is a debug message.")
    logging.info("This is an informational message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
