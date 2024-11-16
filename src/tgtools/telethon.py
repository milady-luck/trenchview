import os

from telethon import TelegramClient

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")


def build_telethon_client(name: str):
    return TelegramClient(name, API_ID, API_HASH)
