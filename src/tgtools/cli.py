import asyncio
import logging
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import click

from tgtools.parsing import parse_coin_call
from tgtools.scraping import get_recent_rickbot_messages
from tgtools.telethon import build_telethon_client


def setup_logging(log_level, log_file=None):
    """Configure logging for both file and console output"""
    # Create logger with a namespace that matches your application
    logger = logging.getLogger("tgtools")
    logger.setLevel(log_level)

    # Prevent duplicate logs by checking if handlers already exist
    if not logger.handlers:
        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        simple_formatter = logging.Formatter("%(levelname)s: %(message)s")

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=1024 * 1024, backupCount=3
            )
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)

    return logger


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    help="Set the logging level",
)
@click.option("--log-file", type=click.Path(), help="Optional log file path")
def cli(log_level, log_file):
    """Async CLI tool."""
    setup_logging(log_level, log_file)


async def _recent_calls(tg_client, group_id, prev_time):
    rickbot_messages = await get_recent_rickbot_messages(tg_client, group_id, prev_time)
    coin_calls = [
        c for c in [parse_coin_call(m) for m in rickbot_messages] if c is not None
    ]

    return coin_calls


@cli.command()
@click.option("--mins", default=60)
@click.option("--group-id", default=-1001639107971)  # default to the lab
def recent_calls(mins, group_id):
    logger = logging.getLogger("tgtools")
    tg_client = build_telethon_client("tgtools-recent-calls")

    prev_time = datetime.now() - timedelta(minutes=mins)

    loop = asyncio.get_event_loop()
    calls = loop.run_until_complete(
        # TODO: make this a composition with parsing, formatting
        _recent_calls(tg_client, group_id, prev_time)
    )
    logger.info(f"{len(calls)} calls found")

    # TODO: format calls
    # click.echo(calls)
    # TODO: remove
    # for m in calls:
    #     print(m.resp_msg.message)


if __name__ == "__main__":
    cli()
