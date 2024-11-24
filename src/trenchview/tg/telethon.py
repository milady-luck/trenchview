import os

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")

SESSION_STR = os.getenv("TG_SESSION")


def build_telethon_client(name: str):
    if SESSION_STR:
        # FIXME: might be better to handle this in caller
        return TelegramClient(StringSession(SESSION_STR), API_ID, API_HASH)
    else:
        return TelegramClient(name, API_ID, API_HASH)
