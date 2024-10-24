import logging
import os


def create_config_file(filename: str, config_data: dict):
	"""
	Create or overwrite a configuration file with the provided settings.

	Args:
		filename (str): The name of the config file.
		config_data (dict): A dictionary containing config key-value pairs.
	"""
	try:
		dir_name = os.path.dirname(filename)
		os.makedirs(dir_name, exist_ok=True)

		with open(filename, 'w') as config_file:
			for key, value in config_data.items():
				config_file.write(f"{key}={value}\n")

		logging.info(f"Configuration file {filename} created successfully.")
	except Exception as e:
		logging.error(f"Error creating config file {filename}: {e}")


def create_env(secret_key: str, bot_token: str, algorithm: str = 'SHA256',
               db_user: str = '', db_password: str = '',
               db_host: str = '', db_name: str = ''):
	"""
	Create a configuration file for crypto settings and database connection.

	:param:secret_key (str): The secret key for crypto.
		bot_token (str):
		algorithm (str): The algorithm used for crypto (default is 'SHA256').
		db_user (str): The database user (default is empty).
		db_password (str): The database password (default is empty).
		db_host (str): The database host (default is empty).
		db_name (str): The database name (default is empty).
	"""
	config_data = {
		'SECRET_KEY': secret_key,
		'BOT_TOKEN': bot_token,
		'ALGORITHM': algorithm,
		'DB_USER': db_user,
		'DB_PASSWORD': db_password,
		'DB_HOST': db_host,
		'DB_PORT': '5432',  # Default PostgreSQL port
		'DB_NAME': db_name,
	}

	env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", '.env')
	create_config_file(env_file_path, config_data)
