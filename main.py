import asyncio
import contextlib
import logging
import sys
import functools
import typer

cli = typer.Typer(no_args_is_help=True)


def handle_command_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
            typer.echo(f"Error in {func.__name__}: {e}", err=True)
            sys.exit(1)
    return wrapper


@cli.command(help="Run the bot")
@handle_command_errors
def run_bot() -> None:
    """
    Command to run the bot.
    """
    from app.app import initialize_application
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(initialize_application())


if __name__ == '__main__':
    cli()
