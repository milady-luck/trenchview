import click

# from . import core


@click.group()
def cli():
    """Async CLI tool."""
    pass


@cli.command()
def recent_calls():
    click.echo("hello world")


if __name__ == "__main__":
    cli()
