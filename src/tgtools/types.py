from datetime import datetime
from typing import NamedTuple


class UnparsedRickbotCall(NamedTuple):
    caller: str

    rickbot_message: str
    dt: datetime


# TODO: this should *only* exist in parsing. move it over there
# NOTE: holds just the information for formatted output
class CoinCall(NamedTuple):
    caller: str
    ticker: str
    call_fdv: float

    dt: datetime

    # resp_url: str
