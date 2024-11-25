from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple


class UnparsedRickbotCall(NamedTuple):
    caller: str

    rickbot_message: str
    dt: datetime


# NOTE: holds just the information for formatted output
class CoinCall(NamedTuple):
    caller: str

    # TODO: add CA
    ticker: str
    chain: str
    fdv: float

    dt: datetime


class CoinClass(Enum):
    BLUE_CHIP = auto()
    MID_CAP = auto()
    SMALL_CAP = auto()
    SHITTER = auto()


def fdv_to_class(fdv: float) -> CoinClass:
    if fdv > 250_000_000:
        return CoinClass.BLUE_CHIP
    elif fdv > 25_000_000:
        return CoinClass.MID_CAP
    elif fdv > 5_000_000:
        return CoinClass.SMALL_CAP
    else:
        return CoinClass.SHITTER


def call_to_class(coin_call: CoinCall):
    return fdv_to_class(coin_call.fdv)
