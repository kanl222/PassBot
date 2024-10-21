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


def create_crypto_config(secret_key: str, algorithm: str = 'SHA256'):
	"""
	Create a configuration file for crypto settings.

	Args:
		secret_key (str): The secret key for crypto.
		algorithm (str): The algorithm used for crypto (default is 'SHA256').
	"""
	config_data = {
		'SECRET_KEY': secret_key,
		'ALGORITHM': algorithm
	}
	create_config_file('../.config_crypto', config_data)


def create_db_config(db_user: str, db_password: str, db_host: str, db_name: str, is_postgresql: bool = False):
	"""
	Create a configuration file for database settings.

	Args:
		db_user (str): The database username.
		db_password (str): The database password.
		db_host (str): The database host.
		db_name (str): The name of the database.
		is_postgresql (bool): Whether PostgreSQL is used (default is False).
	"""
	config_data = {
		'DB_USER': db_user,
		'DB_PASSWORD': db_password,
		'DB_HOST': db_host,
		'DB_PORT': '5432' if is_postgresql else '',  # Default to 5432 for PostgreSQL
		'DB_NAME': db_name,
		'IS_POSTGRESQL': str(is_postgresql)
	}
	create_config_file('../.config_db', config_data)

# create_crypto_config(secret_key="mysecretkey")
# create_db_config(db_user="dbuser", db_password="dbpassword", db_host="localhost", db_name="mydatabase", is_postgresql=True)
