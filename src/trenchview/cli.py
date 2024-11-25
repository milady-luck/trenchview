import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

import click

from trenchview.cmds import get_recent_tg_calls
from trenchview.formatting import (
    format_calls,
    group_by_ticker_chain,
    print_telethon_obj,
)
from trenchview.logger import setup_logging
from trenchview.tg.scraping import (
    get_last_msg,
)
from trenchview.tg.telethon import build_telethon_client


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="ERROR",
    help="Set the logging level",
)
@click.option("--log-file", type=click.Path(), help="Optional log file path")
def cli(log_level, log_file):
    """Async CLI tool."""
    setup_logging(log_level, log_file)


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
    logger = logging.getLogger("trenchview.cli")
    if days == 0 and hours == 0 and mins == 0:
        td = timedelta(hours=1)
    else:
        td = timedelta(days=days, hours=hours, minutes=mins)

    prev_time = datetime.now(UTC) - td

    tg_client = build_telethon_client("trenchview-recent-calls")

    loop = asyncio.get_event_loop()
    calls = loop.run_until_complete(get_recent_tg_calls(tg_client, group_id, prev_time))
    logger.info(f"{len(calls)} calls found")

    ticker_chain_to_calls = group_by_ticker_chain(calls, multi_only)

    if out_file:
        f = Path(out_file)
        with f.open("w") as w:
            json.dump(ticker_chain_to_calls, w, indent=2)

    else:
        print(format_calls(ticker_chain_to_calls))


@cli.command()
@click.option("--group-id", default=-1001639107971)  # default to the lab
def last_msg(group_id):
    # NOTE: testing method just to see what latest message format is
    tg_client = build_telethon_client("trenchview-last-msg")

    loop = asyncio.get_event_loop()
    message = loop.run_until_complete(get_last_msg(tg_client, group_id))

    print_telethon_obj(message)


if __name__ == "__main__":
    cli()
