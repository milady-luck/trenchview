import logging
from datetime import datetime

from telethon import TelegramClient

from trenchview.types import UnparsedRickbotCall

# NOTE: assuming this is static for now
RICK_ID = 6126376117


async def get_last_msg(client: TelegramClient, group_id: int):
    logger = logging.getLogger("trenchview.tg.scraping")

    async with client:
        logger.info(f"getting last message in {group_id}")

        group = await client.get_entity(group_id)
        messages = await client.get_messages(
            group,
        )

        if len(messages) > 0:
            return messages[0]

        else:
            return None


# NOTE: gets rickbot messages + rick caller (i.e. joins appropriately)
async def get_recent_rickbot_calls(
    client: TelegramClient, group_id: int, start_time: datetime
) -> list[UnparsedRickbotCall]:
    logger = logging.getLogger("trenchview.tg.scraping")

    async with client:
        logger.info(
            f"getting recent rickbot messages from {group_id} since {start_time}"
        )
        group = await client.get_entity(group_id)
        messages = await client.get_messages(
            group,
            reverse=True,  # necessary for offset_date to be min_date
            offset_date=start_time,
            max_id=0,
            min_id=0,
        )
        logger.info(f"got {len(messages)} total messages")
        id_to_msg = {msg.id: msg for msg in messages}
        rick_msgs = [msg for msg in messages if msg.from_id.user_id == RICK_ID]

        logger.info(f"got {len(rick_msgs)} rickbot messages")

        # for all rickbot messages, get the parent message too and create a
        # UnparsedRickbotCall
        ret = []
        for msg in rick_msgs:
            # only include callers for messages whose caller is *also* in the window
            if msg.reply_to_msg_id and msg.reply_to_msg_id in id_to_msg:
                call_msg = id_to_msg[msg.reply_to_msg_id]
                caller = call_msg.sender.username

                ret.append(UnparsedRickbotCall(caller, msg.message, msg.date))

        logger.info("added caller for relevant messages")

        return ret
