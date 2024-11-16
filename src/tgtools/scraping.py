import asyncio
import json
import logging
import os
from datetime import datetime, timedelta

from telethon import TelegramClient

from tgtools.types import TgMessage, TgRickbotMessage, TgUser

# NOTE: assuming this is static for now
RICK_NAME = "RickBurpBot"
RICK_ID = 6126376117


# NOTE: gets rickbot messages + rick caller
async def get_recent_rickbot_messages(
    client: TelegramClient, group_id: int, start_time: datetime
) -> list[TgRickbotMessage]:
    logger = logging.getLogger(__name__)

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

        # for all rickbot messages, get the parent message too and create a TgRickbotMessage
        ret = []
        for msg in rick_msgs:
            # rick message
            call_msg = None
            resp_msg = TgMessage(msg.id, TgUser(RICK_ID, RICK_NAME), msg.message)

            if msg.reply_to_msg_id:
                logger.info(f"adding caller for msg {msg.reply_to_msg_id}")
                # if call message in id_to_msg, great. if not, go get it and add to map
                reply_to_id = msg.reply_to_msg_id
                if msg.reply_to_msg_id in id_to_msg:
                    call_msg = await TgMessage.from_telethon_msg(
                        client, id_to_msg[msg.reply_to_msg_id]
                    )

                else:
                    call_msg = await TgMessage.from_id(client, reply_to_id)

            ret.append(TgRickbotMessage(call_msg, resp_msg))

        return ret
