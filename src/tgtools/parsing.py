# diff message categories:
# calls, price checks, tweets, ads

import re
from typing import NamedTuple

TICKER_RE = r"(?:^|\s)\$(\w+)(?:\s|$)"
EX_CHAIN_RE = r"(\w+)\s+@\s+(\w+)"
FDV_RE = r"\$(\d+(?:\.\d+)?[mbk]?)"


class PriceCheck(NamedTuple):
    url: str
    # caller_username: str # TODO:

    ticker: str
    chain: str
    exchange: str

    call_fdv: float
    ath_fdv: float

    def _fdv_str_to_float(fdv_str):
        pass

    # should this be an async method that takes client too? for replyor?
    # I think we can test faster if I can just have the full (relevant) graph in here
    def from_rick_msg(rick_msg):
        lines = rick_msg.splitlines()

        ticker_match = re.search(TICKER_RE, lines[0])
        if not ticker_match:
            print(f"couldn't find ticker in {rick_msg}")
            return None
        ticker = ticker_match.group(1)

        ex_chain_match = re.search(EX_CHAIN_RE, lines[1])
        if not ex_chain_match:
            print(f"couldn't find chain/exchange str in {rick_msg}")
            return None
        chain, exchange = ex_chain_match.group(1), ex_chain_match.group(2)

        call_fdv_match = re.search(FDV_RE, lines[3])
        if not call_fdv_match:
            print(f"couldn't find call fdv in {rick_msg}")
            return None
        call_fdv = call_fdv_match.group(1)

        ath_fdv_match = re.search(FDV_RE, lines[6])
        if not ath_fdv_match:
            print(f"couldn't find ath fdv in {rick_msg}")
            return None
        ath_fdv = ath_fdv_match.group(1)

        return PriceCheck("TODO", ticker, chain, exchange, call_fdv, ath_fdv)


def is_price_check(rick_msg):
    num_lines = len(rick_msg.message.splitlines())
    return num_lines >= 15


# TODO: extract all msg types here I guess
def convert_msg(rick_msg):
    if is_price_check(rick_msg):
        return PriceCheck.from_rick_msg(rick_msg)

    return None


def convert_msgs(msgs):
    pass


# NOTE: this should be moved to a test file
def check_test_msgs():
    with open("test_data/rick_msgs.txt") as f:
        rick_msgs = f.read().splitlines()

    from collections import defaultdict

    count_to_msgs = defaultdict(list)
    for msg in rick_msgs:
        escaped_msg = msg.encode().decode("unicode-escape")
        num_lines = len(escaped_msg.splitlines())
        count_to_msgs[num_lines].append(msg)

    print(count_to_msgs.keys())

    for count, msgs in count_to_msgs.items():
        print(f"count: {count}")
        for msg in msgs:
            print(msg)
        print()


# check_test_msgs()

# rick_msg = "\ud83d\udc26 L1quidated: tweet from topchimper \u22c5 3h ago\n\ud83d\udcac 15 \ud83d\udd01 6 \u2764\ufe0f 97 \ud83d\udc40 3K \u267b\ufe0f \u2139\ufe0f"
# pc = PriceCheck.from_rick_msg(rick_msg.encode('utf-8', errors='replace').decode('utf-8'))

# print(pc)
