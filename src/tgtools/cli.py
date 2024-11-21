import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path

import click
from tabulate import tabulate

from tgtools.formatting import (
    coincall_to_row,
    group_by_ticker,
    print_telethon_obj,
)
from tgtools.parsing import parse_coin_call
from tgtools.scraping import (
    get_last_msg,
    get_recent_rickbot_calls,
)
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
    rickbot_calls = await get_recent_rickbot_calls(tg_client, group_id, prev_time)
    coin_calls = [
        c for c in [parse_coin_call(m) for m in rickbot_calls] if c is not None
    ]

    return coin_calls


# NOTE: this may belong in 'formatting'
@cli.command()
@click.option("--days", "-d", type=int, default=0, help="Number of days (default: 0)")
@click.option("--hours", "-h", type=int, default=0, help="Number of hours (default: 0)")
@click.option(
    "--mins", "-m", type=int, default=0, help="Number of minutes (default: 0)"
)
@click.option("--group-id", default=-1001639107971)  # default to the lab
@click.option("--out-file", "-o", default=None)
@click.option(
    "--multi-only",
    "-mo",
    is_flag=True,
    help="Filter to only those tickers called >1 time",
)
def recent_calls(days, hours, mins, group_id, out_file, multi_only):
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

    ticker_to_calls = group_by_ticker(calls, multi_only)

    if out_file:
        f = Path(out_file)
        with f.open("w") as w:
            json.dump(ticker_to_calls, w, indent=2)

    else:
        # display tickers in reverse max fdv order
        sorted_tickers = sorted(
            ticker_to_calls.items(),
            key=lambda kv: max([call.fdv for call in kv[1]]),
            reverse=True,
        )
        for ticker, calls in sorted_tickers:
            print(ticker)
            print(tabulate([coincall_to_row(call) for call in calls]))
            print()


@cli.command()
@click.option("--group-id", default=-1001639107971)  # default to the lab
def last_msg(group_id):
    # NOTE: testing method just to see what latest message format is
    tg_client = build_telethon_client("tgtools-last-msg")

    loop = asyncio.get_event_loop()
    message = loop.run_until_complete(get_last_msg(tg_client, group_id))

    print_telethon_obj(message)


if __name__ == "__main__":
    cli()
