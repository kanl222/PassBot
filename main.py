import sys

import typer

import app

cli = typer.Typer()


# Функции команд
@cli.command(help="Initialize database models")
def init_db_models(db_url: str = typer.Option(..., help="URL of the database")):
	try:
		typer.echo(f"Initializing database models at {db_url}...")
		app.db_init_models()
		typer.echo("Database models initialized successfully.")
	except Exception as e:
		typer.echo(f"Error initializing database models: {e}", err=True)
		sys.exit(1)


@cli.command(help="Initialize user")
def init_user(username: str = typer.Option(..., help="User login"),
              password: str = typer.Option(..., help="User password")):
	try:
		typer.echo(f"Initializing user with login: {username}")
		app.init_user(username, password)
		typer.echo("User initialized successfully.")
	except Exception as e:
		typer.echo(f"Error initializing user: {e}", err=True)
		sys.exit(1)


@cli.command(help="Run the bot")
def run_bot():
	try:
		typer.echo("Running the bot...")
		app.run_bot()
		typer.echo("Bot is running.")
	except Exception as e:
		typer.echo(f"Error running the bot: {e}", err=True)
		sys.exit(1)


if __name__ == '__main__':
	cli()
