from logging.config import dictConfig

def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            },
            "detailed": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
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
            "level": "INFO",
            "handlers": ["console", "file"]
        },
        "loggers": {
            "bot_telegram": {
                "level": "WARNING",
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    }

    dictConfig(logging_config)
