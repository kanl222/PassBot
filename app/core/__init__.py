from logging import error, info



__name__ = 'core'


def initialization_settings() -> None:
	"""
	Initialize application settings and validate the environment.

	:raises Exception: If any settings are not configured correctly.
	"""
	info("Initializing application settings...")
	try:
		from .settings import settings
		from .security import settings_crypto
		info("Application settings initialized successfully.")

	except ValueError as ve:
		error(f"Configuration error: {ve}", exc_info=True)
		raise
	except Exception as e:
		error(f"Error during settings initialization: {e}", exc_info=True)
		raise
