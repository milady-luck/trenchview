import asyncio
import logging
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import click

from tgtools.formatting import discover_and_print, format_coin_calls
from tgtools.parsing import parse_coin_call
from tgtools.scraping import get_last_msg, get_recent_rickbot_messages
from tgtools.telethon import build_telethon_client


def setup_logging(log_level, log_file=None):
    """Configure logging for both file and console output"""
    # Create logger with a namespace that matches your application
    logger = logging.getLogger("tgtools")
    logger.setLevel(log_level)

    # Prevent duplicate logs by checking if handlers already exist
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=1024 * 1024, backupCount=3
            )
            file_handler.setFormatter(formatter)
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
@click.option("--days", "-d", type=int, default=0, help="Number of days (default: 0)")
@click.option("--hours", "-h", type=int, default=0, help="Number of hours (default: 0)")
@click.option(
    "--mins", "-m", type=int, default=0, help="Number of minutes (default: 0)"
)
@click.option("--group-id", default=-1001639107971)  # default to the lab
def recent_calls(days, hours, mins, group_id):
    logger = logging.getLogger("tgtools")

    if days == 0 and hours == 0 and mins == 0:
        td = timedelta(hours=1)
    else:
        td = timedelta(days=days, hours=hours, minutes=mins)

    prev_time = datetime.now() - td

    tg_client = build_telethon_client("tgtools-recent-calls")

    loop = asyncio.get_event_loop()
    calls = loop.run_until_complete(_recent_calls(tg_client, group_id, prev_time))
    logger.info(f"{len(calls)} calls found")

    print(format_coin_calls(calls))


@cli.command()
@click.option("--group-id", default=-1001639107971)  # default to the lab
def last_msg(group_id):
    # NOTE: testing method just to see what latest message format is
    tg_client = build_telethon_client("tgtools-last-msg")

    loop = asyncio.get_event_loop()
    message = loop.run_until_complete(get_last_msg(tg_client, group_id))

    discover_and_print(message)


if __name__ == "__main__":
    cli()
