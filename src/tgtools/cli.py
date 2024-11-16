import asyncio
from datetime import datetime, timedelta

import click

from tgtools.parsing import parse_coin_call
from tgtools.scraping import get_recent_rickbot_messages
from tgtools.telethon import build_telethon_client


@click.group()
def cli():
    """Async CLI tool."""
    pass


async def get_recent_calls(tg_client, group_id, prev_time):
    rickbot_messages = await get_recent_rickbot_messages(tg_client, group_id, prev_time)
    coin_calls = [
        c for c in [parse_coin_call(m) for m in rickbot_messages] if c is not None
    ]

    return coin_calls


@cli.command()
@click.option("--mins", default=60)
@click.option("--group-id", default=-1001639107971)  # default to the lab
def recent_calls(mins, group_id):
    tg_client = build_telethon_client("tgtools-recent-calls")

    prev_time = datetime.now() - timedelta(minutes=mins)

    loop = asyncio.get_event_loop()
    calls = loop.run_until_complete(
        # TODO: make this a composition with parsing, formatting
        get_recent_calls(tg_client, group_id, prev_time)
    )

    # TODO: format calls
    click.echo(calls)
    click.echo("hello world")


if __name__ == "__main__":
    cli()
