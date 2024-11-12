from telethon import TelegramClient
from collections import defaultdict
from datetime import datetime, timedelta

from rick import get_rick_msgs, is_price_check

import asyncio
import os
import sys
import json

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")

TARGET_GROUP_ID = -1001639107971 # replace with group of your choice

MSG_PERIOD = timedelta(minutes=1)
PREV_TIME = datetime.now() - MSG_PERIOD

async def main():
    # testing group scraping
    client = TelegramClient('coin-mentions', API_ID, API_HASH)

    async with client:
        print("connected to tg")
        group = await client.get_entity(TARGET_GROUP_ID)
        
        print(f"scraping group: {group.title} for RickBurpBot messages since {PREV_TIME}")
        rick_msgs = await get_rick_msgs(client, group, PREV_TIME)
        print(f"found {len(rick_msgs)} rickbot messages")
        
        price_checks = [msg for msg in rick_msgs if is_price_check(msg)]
        print(f"found {len(price_checks)} price checks")
        print([msg.message for msg in price_checks])

        # print(rick_msgs)

# NOTE: not for external use
async def gen_test_rick_msgs():
    client = TelegramClient('coin-mentions', API_ID, API_HASH)

    async with client:
        group = await client.get_entity(TARGET_GROUP_ID)
        rick_msgs = await get_rick_msgs(client, group, PREV_TIME)

        with open("test_data/rick_msgs.txt", "w") as f:
            json.dump([msg.message for msg in rick_msgs], f, indent=4)

loop = asyncio.get_event_loop()
loop.run_until_complete(gen_test_rick_msgs())