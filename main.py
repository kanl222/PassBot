import logging
import sys
import typer
from sqlalchemy.sql.operators import from_

cli = typer.Typer(no_args_is_help=True)


@cli.command(help="Create configuration files")
def create_configs():
    """
    Command to generate config files for the application.
    """
    try:
        from app.tools.create_config import create_config_files

        create_env(bot_token="YOUR_BOT_TOKEN", db_user="DB_USER",
                       db_password="DB_PASSWORD")
        logging.info("Configuration files created successfully.")

    except Exception as e:
            logging.error(f"Error creating configuration files: {e}", exc_info=True)
            typer.echo(f"Error creating configuration files: {e}", err=True)
            sys.exit(1)


@cli.command(help="Initialize database models")
def init_db_models():
    """
    Command to initialize the database models.
    """
    from app.app import db_init_models
    try:
        db_init_models()
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
    from app.app import init_user
    try:
        init_user(username, password)
    except Exception as e:
        logging.error(f"Error initializing user: {e}", exc_info=True)
        typer.echo(f"Error initializing user: {e}", err=True)
        sys.exit(1)


@cli.command(help="Run the bot")
def run_bot():
    """
    Command to run the bot.
    """
    from app.app import run_bot
    try:
        run_bot()
    except Exception as e:
        logging.error(f"Error running the bot: {e}", exc_info=True)
        typer.echo(f"Error running the bot: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
