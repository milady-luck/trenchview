import logging
from datetime import datetime

from telethon import TelegramClient

from tgtools.types import TgMessage, TgRickbotMessage, TgUser

# NOTE: assuming this is static for now
RICK_NAME = "RickBurpBot"
RICK_ID = 6126376117


async def get_last_msg(client: TelegramClient, group_id: int):
    logger = logging.getLogger("tgtools")

    async with client:
        logger.debug(f"getting last message in {group_id}")

        group = await client.get_entity(group_id)
        messages = await client.get_messages(
            group,
        )

        if len(messages) > 0:
            return messages[0]

        else:
            return None


# NOTE: gets rickbot messages + rick caller
async def get_recent_rickbot_messages(
    client: TelegramClient, group_id: int, start_time: datetime
) -> list[TgRickbotMessage]:
    logger = logging.getLogger("tgtools")

    async with client:
        logger.debug(
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
        logger.debug(f"got {len(messages)} total messages")
        id_to_msg = {msg.id: msg for msg in messages}
        rick_msgs = [msg for msg in messages if msg.from_id.user_id == RICK_ID]
        logger.debug(f"got {len(rick_msgs)} rickbot messages")

        # NOTE: for 1-2 day scrapes, this is the thing that takes all the time
        # for all rickbot messages, get the parent message too and create a
        # TgRickbotMessage
        ret = []
        for msg in rick_msgs:
            call_msg = None
            resp_msg = TgMessage(
                msg.id, TgUser(RICK_ID, RICK_NAME), msg.message, msg.date
            )

            # only include callers for messages whose caller is *also* in the window
            if msg.reply_to_msg_id and msg.reply_to_msg_id in id_to_msg:
                # TODO: retry logic here to avoid floodwait errors

                # get user for message, add as caller
                call_msg = await TgMessage.from_telethon_msg(
                    client, id_to_msg[msg.reply_to_msg_id]
                )

            ret.append(TgRickbotMessage(call_msg, resp_msg))
        logger.debug("added caller for relevant messages")

        return ret