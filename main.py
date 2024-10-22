import sys
import typer
import logging
import app

cli = typer.Typer()


@cli.command(help="Create configuration files")
def create_configs():
	"""
	Command to generate config files for the application.
	"""
	try:
		typer.echo("Creating configuration files...")
		app.create_config_files()
		typer.echo("Configuration files created successfully.")
	except Exception as e:
		logging.error(f"Error creating configuration files: {e}", exc_info=True)
		typer.echo(f"Error creating configuration files: {e}", err=True)
		sys.exit(1)


@cli.command(help="Initialize database models")
def init_db_models():
	"""
	Command to initialize the database models.
	"""
	try:
		typer.echo(f"Initializing database models at {app.get_db_url()}...")
		app.db_init_models()
		typer.echo("Database models initialized successfully.")
	except Exception as e:
		logging.error(f"Error initializing database models: {e}", exc_info=True)
		typer.echo(f"Error initializing database models: {e}", err=True)
		sys.exit(1)


@cli.command(help="Initialize user")
def init_user(username: str = typer.Option(..., help="User login"),
              password: str = typer.Option(..., help="User password")):
	"""
	Command to initialize a user for parsing or other operations.

	:param username: The user's login.
	:param password: The user's password.
	"""
	try:
		typer.echo(f"Initializing user with login: {username}")
		app.init_user(username, password)
		typer.echo("User initialized successfully.")
	except Exception as e:
		logging.error(f"Error initializing user: {e}", exc_info=True)
		typer.echo(f"Error initializing user: {e}", err=True)
		sys.exit(1)


@cli.command(help="Run the bot")
def run_bot():
	"""
	Command to run the bot.
	"""
	try:
		typer.echo("Running the bot...")
		app.run_bot()
		typer.echo("Bot is running.")
	except Exception as e:
		logging.error(f"Error running the bot: {e}", exc_info=True)
		typer.echo(f"Error running the bot: {e}", err=True)
		sys.exit(1)


if __name__ == '__main__':
	cli()
