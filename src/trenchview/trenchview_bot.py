import logging
import os
import re
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import humanize
from telegram import Update
from telegram.error import Conflict
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from trenchview.cmds import get_recent_tg_calls
from trenchview.formatting import format_calls, group_by_ticker_chain, group_into_parts
from trenchview.logger import setup_logging
from trenchview.tg.telethon import build_telethon_client

BOT_TOKEN = os.getenv("TRENCHVIEW_BOT_TOKEN")

DEFAULT_DURATION = timedelta(hours=1)
DEFAULT_TZ = ZoneInfo("America/Los_Angeles")

# tg max response length
MAX_RESP_LEN = 4095

LAB_USER_IDS = [int(x) for x in os.getenv("TRENCHVIEW_LAB_USER_IDS").split()]


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
    # TODO: may make sense in the future to make this a decorator
    logger = logging.getLogger("trenchview.bot")

    user = update.effective_user
    logger.info(f"received message from user {user.username}")

    if user.id not in LAB_USER_IDS:
        await update.message.reply_text("you're not authorized to call this method!")
        return

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

        ticker_chain_to_calls = group_by_ticker_chain(calls)

        raw_msg = format_calls(ticker_chain_to_calls)
        logger.info(f"raw msg len: {len(raw_msg)}")
        if len(raw_msg) <= MAX_RESP_LEN:
            await update.message.reply_text(raw_msg)

        else:
            parts = group_into_parts(raw_msg, MAX_RESP_LEN)
            for part in parts:
                await update.message.reply_text(part)

    except Exception as e:
        logger.error(f"error: {e}")
        logger.error(traceback.format_exc())
        await update.message.reply_text("unknown error! dm @paperun on tg for details")


def error_handler(logger):
    def _error_handler(update, context):
        # TODO: more here when I see errors
        logger.error(f"Update {update} caused error {context.error}")
        if isinstance(context.error, Conflict):
            logger.error("Multiple bot instances detected!")

    return _error_handler


def main():
    setup_logging(logging.INFO)
    logger = logging.getLogger("trenchview.bot")

    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("recent_calls", recent_calls_command))
    app.add_error_handler(error_handler(logger))

    # Start the bot
    logger.info("trenchview-bot is running...")
    logger.info(f"{len(LAB_USER_IDS)} lab users found")
    app.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
