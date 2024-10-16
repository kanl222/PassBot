import typer

cli = typer.Typer()


@cli.command()
def init_db_models():
    pass

@cli.command()
def init_user():
    pass


@cli.command()
def run_bot():
    pass


if __name__ == '__main__':
    cli()