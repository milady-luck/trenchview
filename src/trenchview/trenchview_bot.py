import os
import re
from datetime import UTC, datetime, timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from trenchview.cmds import get_recent_tg_calls
from trenchview.formatting import format_ticker_calls, group_by_ticker
from trenchview.tg.telethon import build_telethon_client

BOT_TOKEN = os.getenv("TRENCHVIEW_BOT_TOKEN")


def parse_duration(dur_str) -> timedelta:
    # TODO: test
    if not dur_str:
        return timedelta(hours=1)

    # Clean up input
    text = dur_str.lower().strip()

    # Handle simple numbers as hours
    if text.isdigit():
        return timedelta(hours=int(text))

    total_seconds = 0
    parts = re.findall(r"(\d+[hm])", text)

    if not parts:
        return timedelta(hours=1)

    for part in parts:
        number = int(part[:-1])
        unit = part[-1]
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
    # NOTE: may want to log slightly cleverly here

    duration = timedelta(hours=1)  # default 1h
    if context.args:
        try:
            duration = parse_duration(context.args[0])

        except ValueError:
            await update.message.reply_text(
                "Couldn't understand duration, using default 1 hour.\n"
                "Use format: 30m, 2h, 1h30m, etc."
            )

    group_id = -1001639107971  # TODO: make this an arg eventually?
    tg_client = build_telethon_client("trenchview-bot-recent-calls")

    prev_time = datetime.now(UTC) - duration
    # logger on query starting
    calls = await get_recent_tg_calls(tg_client, group_id, prev_time)
    # logger on results found

    ticker_to_calls = group_by_ticker(calls)
    await update.message.reply_text(format_ticker_calls(ticker_to_calls))


def main():
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("recent_calls", recent_calls_command))

    # Start the bot
    print("Bot is running...")
    app.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
