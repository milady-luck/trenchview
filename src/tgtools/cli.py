import click
import asyncio
from pathlib import Path
from typing import Optional

# from . import core

@click.group()
def cli():
    """Async CLI tool."""
    pass

@cli.command()
# @click.argument('input_dir', type=click.Path(exists=True))
# @click.option('--workers', '-w', default=4, help='Number of worker tasks')
def recent_calls():
    # use scraping to get all relevant items (incl. reply-tos)
    # use parsing to get data
    # format it, save it
    click.echo('hello world')