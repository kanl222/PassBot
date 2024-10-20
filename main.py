import sys

import typer

try:
	import app
except Exception as e:
	print(e)

cli = typer.Typer()


@cli.command(help="Initialize database models")
async def init_db_models():
	try:
		typer.echo(f"Initializing database models at {app.get_db_url()}...")
		await app.db_init_models()
		typer.echo("Database models initialized successfully.")
	except Exception as e:
		typer.echo(f"Error initializing database models: {e}", err=True)
		sys.exit(1)


@cli.command(help="Initialize user")
async def init_user(username: str = typer.Option(..., help="User login"),
                    password: str = typer.Option(..., help="User password")):
	try:
		typer.echo(f"Initializing user with login: {username}")
		await app.init_user(username, password)
		typer.echo("User initialized successfully.")
	except Exception as e:
		typer.echo(f"Error initializing user: {e}", err=True)
		sys.exit(1)


@cli.command(help="Run the bot")
async def run_bot():
	try:
		typer.echo("Running the bot...")
		await app.run_bot()
		typer.echo("Bot is running.")
	except Exception as e:
		typer.echo(f"Error running the bot: {e}", err=True)
		sys.exit(1)


if __name__ == '__main__':
	cli()
