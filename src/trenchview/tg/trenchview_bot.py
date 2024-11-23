import os
import re
from datetime import timedelta

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("TG_BOT_TOKEN")


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

    await update.message.reply_text(f"⏳ Duration: {format_duration(duration)}")


def main():
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("recent_calls", recent_calls_command))

    # Start the bot
    print("Bot is running...")
    app.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
