import logging
from pathlib import Path
from typing import Optional, Dict
from contextlib import suppress

def create_config_files() -> None:
    """Create configuration files with minimal overhead."""
    try:
        create_env()
        logging.info("Configuration files created successfully.")
    except Exception as e:
        logging.error(f"Error creating configuration files: {e}", exc_info=True)
        raise

def create_config_file(filepath: Path, config_data: Dict[str, str]) -> None:
    """
    Efficiently create or overwrite a configuration file.
    
    Args:
        filepath (Path): Path to the configuration file.
        config_data (Dict[str, str]): Configuration key-value pairs.
    """
    # Ensure directory exists
    with suppress(FileExistsError):
        filepath.parent.mkdir(parents=True)

    # Write configuration efficiently
    filepath.write_text(
        '\n'.join(f"{key}={value}" for key, value in config_data.items())
    )
    logging.info(f"Configuration file '{filepath}' created successfully.")

def create_env(
    secret_key: str = '', 
    bot_token: str = '',
    db_user: Optional[str] = None,
    db_password: Optional[str] = None,
    db_host: Optional[str] = None,
    db_name: Optional[str] = None,
    db_port: str = '5432'
) -> None:
    """
    Create a configuration file with efficient data handling.
    
    Args:
        secret_key (str): Cryptographic secret key.
        bot_token (str): Bot authentication token.
        db_user (str, optional): Database username.
        db_password (str, optional): Database password.
        db_host (str, optional): Database host.
        db_name (str, optional): Database name.
        db_port (str, optional): Database port.
    """
    config_data = {
        key: value or 'None' 
        for key, value in {
            'SECRET_KEY': secret_key,
            'BOT_TOKEN': bot_token,
            'DB_USER': db_user,
            'DB_PASSWORD': db_password,
            'DB_HOST': db_host,
            'DB_PORT': db_port,
            'DB_NAME': db_name
        }.items()
    }

    create_config_file(
        Path(__file__).parent.parent / ".env", 
        config_data
    )
