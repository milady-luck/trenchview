import logging
import re
from typing import NamedTuple

from trenchview.custom_types import (
    CoinCall,
    UnparsedRickbotCall,
)

EX_CHAIN_RE = r"(\w+)\s+@\s+(\w+)"
FDV_RE = r"\$(\d+(?:\.\d+)?(?:[KMB])?)"

TICKER_RE = r"(?<=\$)(\$*[^\s]+)"


def find_ticker(line):
    matches = re.findall(TICKER_RE, line)
    if len(matches) == 0:
        return None

    return matches[0]


def parse_fdv(fdv_line):
    # handle K, M, B
    fdv_match = re.search(FDV_RE, fdv_line)
    if not fdv_match:
        return None

    amount_str = fdv_match.group(1)

    multiplier = 1
    if amount_str.endswith("K"):
        multiplier = 1_000
        amount_str = amount_str[:-1]
    elif amount_str.endswith("M"):
        multiplier = 1_000_000
        amount_str = amount_str[:-1]
    elif amount_str.endswith("B"):
        multiplier = 1_000_000_000
        amount_str = amount_str[:-1]

    return float(amount_str) * multiplier


class ParsedCoinCallResp(NamedTuple):
    ticker: str
    chain: str

    call_fdv: float


def parse_coin_call_resp(msg: str) -> ParsedCoinCallResp:
    logger = logging.getLogger("trenchview")

    # TODO: when does this happen?
    if msg is None:
        return None

    lines = msg.splitlines()

    if len(lines) < 15:
        return None

    ticker = find_ticker(lines[0])
    if not ticker:
        return None

    ex_chain_match = re.search(EX_CHAIN_RE, lines[1])
    if not ex_chain_match:
        # TODO: this can happen for pump.fun non-graduated coins!
        logger.warning(f"couldn't find chain/exchange str in {msg}")
        chain = "Unknown"
    else:
        chain = ex_chain_match.group(1)

    call_fdv = parse_fdv(lines[3])
    if not call_fdv:
        logger.warning(f"couldn't find call fdv in {msg}")
        return None

    return ParsedCoinCallResp(ticker, chain, call_fdv)


# NOTE: returns none if not a coin call
def parse_coin_call(msg: UnparsedRickbotCall) -> CoinCall:
    parsed_resp = parse_coin_call_resp(msg.rickbot_message)
    if not parsed_resp:
        return None

    return CoinCall(
        caller=msg.caller,
        ticker=parsed_resp.ticker,
        chain=parsed_resp.chain,
        fdv=parsed_resp.call_fdv,
        dt=msg.dt,
    )
