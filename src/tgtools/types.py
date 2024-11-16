from typing import NamedTuple


class TgUser(NamedTuple):
    uid: int
    uname: str


# NOTE: should I include datetime here too? Probably, for sorting
class TgMessage(NamedTuple):
    msg_id: int

    sender: TgUser
    message: str

    @classmethod
    async def from_telethon_msg(cls, client, telethon_msg):
        # get user from client
        uid = telethon_msg.from_id.user_id

        # NOTE: maybe we don't want to do this every time here! reduce number of
        # get_entity calls
        user = await client.get_entity(uid)
        return cls(telethon_msg.id, TgUser(uid, user.username), telethon_msg.message)

    @classmethod
    async def from_id(cls, client, msg_id):
        msg = await client.get_entity(msg_id)
        return cls.from_telethon_msg(client, msg)


class TgRickbotMessage(NamedTuple):
    call_msg: TgMessage  # NOTE: None implies no caller (i.e. Rickbot ad)
    resp_msg: TgMessage


# TODO: add first caller info?
class ParsedCoinCallResp(NamedTuple):
    ticker: str
    chain: str
    exchange: str

    call_fdv: float
    ath_fdv: float


# NOTE: holds just the information for formatted output
class CoinCall(NamedTuple):
    caller_username: str

    # TODO: datetime?
    resp_url: str

    parsed_resp: ParsedCoinCallResp
