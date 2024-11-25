import logging
import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import humanize
from telegram import Update
from telegram.error import Conflict
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from trenchview.cmds import get_recent_tg_calls
from trenchview.formatting import format_ticker_calls, group_by_ticker
from trenchview.logger import setup_logging
from trenchview.tg.telethon import build_telethon_client

BOT_TOKEN = os.getenv("TRENCHVIEW_BOT_TOKEN")

DEFAULT_DURATION = timedelta(hours=1)
DEFAULT_TZ = ZoneInfo("America/Los_Angeles")


def parse_duration(dur_str) -> timedelta:
    if not dur_str:
        return DEFAULT_DURATION

    # Clean up input
    text = dur_str.lower().strip()

    # Handle simple numbers as hours
    if text.isdigit():
        return timedelta(hours=int(text))

    total_seconds = 0
    parts = re.findall(r"(\d+[dhm])", text)

    if not parts:
        return DEFAULT_DURATION

    for part in parts:
        number = int(part[:-1])
        unit = part[-1]
        if unit == "d":
            total_seconds += number * 86400  # days to seconds
        if unit == "h":
            total_seconds += number * 3600
        elif unit == "m":
            total_seconds += number * 60

    return timedelta(seconds=total_seconds or 3600)


def format_duration(td: timedelta) -> str:
    """Format timedelta in human readable format"""
    total_minutes = td.total_seconds() / 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)

    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    return " and ".join(parts) if parts else "1 hour"  # Fallback to default


async def recent_calls_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger = logging.getLogger("trenchview.bot")

    duration = DEFAULT_DURATION
    user = update.effective_user
    logger.info(f"recent-calls({context.args}) - {user.username}")
    if context.args:
        try:
            duration = parse_duration(context.args[0])

        except ValueError:
            await update.message.reply_text(
                "Couldn't understand duration, using default 1 hour.\n"
                "Use format: 30m, 2h, 1d, 1d2h30m, etc."
            )

    await update.message.reply_text(
        f"working on your request for calls in the last {humanize.precisedelta(duration, minimum_unit='seconds')}"  # noqa: E501
    )

    group_id = -1001639107971  # TODO: make this an arg eventually?

    tg_client = build_telethon_client("trenchview-bot")

    prev_time = datetime.now(DEFAULT_TZ) - duration

    try:
        calls = await get_recent_tg_calls(tg_client, group_id, prev_time)

        ticker_to_calls = group_by_ticker(calls)
        await update.message.reply_text(format_ticker_calls(ticker_to_calls))
    except Exception as e:
        logger.error(f"error: {e}")
        await update.message.reply_text("unknown error! dm @paperun on tg for details")


def error_handler(logger):
    def _error_handler(update, context):
        # TODO: more here when I see errors
        logger.error(f"Update {update} caused error {context.error}")
        if isinstance(context.error, Conflict):
            logger.error("Multiple bot instances detected!")

    return _error_handler(logger)


def main():
    setup_logging(logging.INFO)
    logger = logging.getLogger("trenchview.bot")

    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("recent_calls", recent_calls_command))

    app.add_error_handler(error_handler)

    # Start the bot
    logger.info("trenchview-bot is running...")
    app.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
