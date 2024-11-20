import logging
from datetime import datetime
from typing import NamedTuple

UNKNOWN_FIELD = "UNKNOWN"


class TgUser(NamedTuple):
    uid: int
    uname: str


# NOTE: should I include timestamp here too? Probably, for sorting
# it's .date on the telethon message object
class TgMessage(NamedTuple):
    msg_id: int

    sender: TgUser
    message: str

    dt: datetime

    # FIXME
    # TODO: types *definitely* shouldn't be able to see client
    @classmethod
    async def from_telethon_msg(cls, client, telethon_msg):
        logger = logging.getLogger(
            "tgtools"
        )  # NOTE: definitely should *not* access logger here!

        # get user from client
        uid = telethon_msg.from_id.user_id

        # NOTE: maybe we don't want to do this every time here! reduce number of
        # get_entity calls
        try:
            user = await client.get_entity(uid)
            return cls(
                telethon_msg.id,
                TgUser(uid, user.username),
                telethon_msg.message,
                telethon_msg.date,
            )

        except ValueError:
            logger.warning(f"couldn't find user with id {uid}")
            return cls(
                telethon_msg.id, TgUser(uid, UNKNOWN_FIELD), telethon_msg.message
            )


# TODO: exclude messages w/o a caller and change this to be something more indicative of that
class TgRickbotMessage(NamedTuple):
    call_msg: TgMessage  # NOTE: None implies no caller (i.e. Rickbot ad)
    resp_msg: TgMessage


class ParsedCoinCallResp(NamedTuple):
    ticker: str
    chain: str
    exchange: str

    call_fdv: float


# TODO: simplify this: ticker, caller, call_fdv, timestamp
# NOTE: holds just the information for formatted output
class CoinCall(NamedTuple):
    caller: str
    ticker: str
    call_fdv: float

    dt: datetime

    # resp_url: str
