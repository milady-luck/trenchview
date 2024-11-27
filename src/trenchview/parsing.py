import logging
import re
from typing import NamedTuple

from trenchview.custom_types import (
    CoinCall,
    UnparsedRickbotCall,
)

EX_CHAIN_RE = r"(\w+)\s+@\s+(\w+)"

FDV_RE = r"(\d+(?:\.\d+)?(?:[KMB])?)"

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


ETH_RE = r"0x[a-fA-F0-9]{40}"
SOL_RE = r"[1-9A-HJ-NP-Za-km-z]{32,44}"


def parse_ca(lines):
    for line in lines:
        candidate = line.strip()
        if re.match(ETH_RE, candidate) or re.match(SOL_RE, candidate):
            return candidate

    return None


class ParsedCoinCallResp(NamedTuple):
    ticker: str
    chain: str

    fdv: float

    ca: str


def parse_coin_call_resp(msg: str) -> ParsedCoinCallResp:
    logger = logging.getLogger("trenchview.parsing")

    blocks = msg.strip().split("\n\n")
    if len(blocks) < 2:
        return None

    metrics_block = blocks[0]
    metric_lines = metrics_block.splitlines()
    ticker = find_ticker(metric_lines[0])

    # parse ticker
    if not ticker:
        logger.warning(f"couldn't find ticker in {msg}")
        return None

    # parse chain
    if metric_lines[1].startswith("🌐"):
        ex_chain_match = re.search(EX_CHAIN_RE, metric_lines[1])
        if not ex_chain_match:
            chain = None
        else:
            chain = ex_chain_match.group(1)

    else:
        chain = None

    # parse fdv
    fdv_line = next(line for line in metric_lines if line[0] == "💎")
    if fdv_line is None:
        logger.warning(f"couldn't find fdv in {msg}")
        return None
    else:
        fdv = parse_fdv(fdv_line)

    # parse ca
    ca = parse_ca(msg.strip().splitlines())

    return ParsedCoinCallResp(ticker=ticker, chain=chain, fdv=fdv, ca=ca)


# NOTE: returns none if not a coin call
def parse_coin_call(msg: UnparsedRickbotCall) -> CoinCall:
    parsed_resp = parse_coin_call_resp(msg.rickbot_message)
    if not parsed_resp:
        return None

    return CoinCall(
        caller=msg.caller,
        ticker=parsed_resp.ticker,
        chain=parsed_resp.chain,
        fdv=parsed_resp.fdv,
        ca=parsed_resp.ca,
        dt=msg.dt,
    )
