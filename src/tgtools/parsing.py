# diff message categories:
# calls, price checks, tweets, ads

import re

from tgtools.types import CoinCall, ParsedCoinCallResp, TgRickbotMessage

TICKER_RE = r"(?:^|\s)\$(\w+)(?:\s|$)"
EX_CHAIN_RE = r"(\w+)\s+@\s+(\w+)"
FDV_RE = r"\$(\d+(?:\.\d+)?(?:[KMB])?)"


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


def parse_coin_call_resp(msg: str) -> ParsedCoinCallResp:
    lines = msg.splitlines()

    if len(lines) < 15:
        return None

    ticker_match = re.search(TICKER_RE, lines[0])
    if not ticker_match:
        print(f"couldn't find ticker in {msg}")
        return None
    ticker = ticker_match.group(1)

    ex_chain_match = re.search(EX_CHAIN_RE, lines[1])
    if not ex_chain_match:
        print(f"couldn't find chain/exchange str in {msg}")
        return None
    chain, exchange = ex_chain_match.group(1), ex_chain_match.group(2)

    call_fdv = parse_fdv(lines[3])
    if not call_fdv:
        print(f"couldn't find call fdv in {msg}")
        return None

    ath_fdv = parse_fdv(lines[6])
    if not ath_fdv:
        print(f"couldn't find ath fdv in {msg}")
        return None

    return ParsedCoinCallResp(ticker, chain, exchange, call_fdv, ath_fdv)


# NOTE: returns none if not a coin call
def parse_coin_call(msg: TgRickbotMessage) -> CoinCall:
    return None
