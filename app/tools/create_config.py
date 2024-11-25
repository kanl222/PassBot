import logging
import os
from pathlib import Path
from typing import Optional
ENV_FILE_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".env"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_config_files() -> None:
    """
    Create configuration files for crypto and database settings.
    """
    try:
        create_env()
        logging.info("Configuration files created successfully.")
    except Exception as e:
        logging.error(f"Error creating configuration files: {e}", exc_info=True)
        raise


def create_config_file(filename: str, config_data: dict) -> None:
    """
    Create or overwrite a configuration file with the provided settings.

    Args:
        filename (str): The name of the config file.
        config_data (dict): A dictionary containing config key-value pairs.
    """
    try:
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(filename, 'w') as config_file:
            for key, value in config_data.items():
                config_file.write(f"{key}={value}\n")

        logging.info(f"Configuration file '{filename}' created successfully.")
    except OSError as e:
        logging.error(f"File system error creating config file '{filename}': {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error creating config file '{filename}': {e}", exc_info=True)
        raise


def create_env(secret_key: str = '', bot_token: str = '',
               db_user: Optional[str] = '', db_password: Optional[str] = '',
               db_host: Optional[str] = '', db_name: Optional[str] = '',
               db_port: str = '5432') -> None:
    """
    Create a configuration file for crypto settings and database connection.

    Args:
        secret_key (str): The secret key for cryptographic operations.
        bot_token (str): The bot token for authentication.
        db_user (str, optional): The database user (default is empty).
        db_password (str, optional): The database password (default is empty).
        db_host (str, optional): The database host (default is empty).
        db_name (str, optional): The database name (default is empty).
        db_port (str, optional): The database port (default is '5432').
    """
    config_data = {
        'SECRET_KEY': secret_key,
        'BOT_TOKEN': bot_token,
        'DB_USER': db_user or 'None',
        'DB_PASSWORD': db_password or 'None',
        'DB_HOST': db_host or 'None',
        'DB_PORT': db_port,
        'DB_NAME': db_name or 'None',
    }

    create_config_file(ENV_FILE_PATH, config_data)
