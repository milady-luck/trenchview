from collections import defaultdict
from datetime import datetime
from pprint import pprint

import pytz
from tabulate import tabulate

from trenchview.custom_types import CoinCall

TABLE_ROW_HEADERS = ["caller", "ticker", "call-fdv ($)", "dt"]


DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_dt(dt: datetime):
    local_tz = pytz.timezone("America/Los_Angeles")
    local_dt = dt.astimezone(local_tz)

    return local_dt.strftime(DT_FORMAT)


def coincall_to_row(call: CoinCall) -> list[str]:
    return [
        call.caller,
        f"{call.fdv:,.2f}",
        format_dt(call.dt),
    ]


def print_telethon_obj(obj, depth=5):
    """Print all non-magic attributes of an object and their values. Used for obj
    introspection"""

    def get_value(obj, attr, current_depth):
        if current_depth <= 0:
            return "Max depth reached"
        try:
            value = getattr(obj, attr)
            # Skip if it's callable (method/function)
            if callable(value):
                return None
            if hasattr(value, "__dict__"):
                if current_depth > 1:
                    nested_dict = {
                        k: get_value(value, k, current_depth - 1)
                        for k in dir(value)
                        if not k.startswith("_")
                    }
                    # Remove None values (methods) from nested dict
                    return {k: v for k, v in nested_dict.items() if v is not None}
                return "Nested object"
            return value
        except Exception as e:
            return f"Error accessing: {str(e)}"

    # Get all non-magic attributes
    attributes = [attr for attr in dir(obj) if not attr.startswith("_")]

    # Create dictionary of attribute values, excluding methods
    result = {}
    for attr in attributes:
        value = get_value(obj, attr, depth)
        if value is not None:  # Only add if not a method
            result[attr] = value

    pprint(result, width=80, sort_dicts=False)


def group_by_ticker_chain(
    calls: list[CoinCall], multi_only=False
) -> dict[str, list[CoinCall]]:
    ticker_chain_to_calls: dict[(str, str), list[CoinCall]] = defaultdict(list)
    for call in calls:
        ticker_chain_to_calls[(call.ticker, call.chain)].append(call)

    # sort calls for a given ticker by dt
    ticker_chain_to_calls = {
        ticker_chain: sorted(calls, key=lambda call: call.dt)
        for ticker_chain, calls in ticker_chain_to_calls.items()
    }

    # filter if multicalled only
    if multi_only:
        ticker_chain_to_calls = {
            ticker_chain: calls
            for ticker_chain, calls in ticker_chain_to_calls.items()
            if len(calls) > 1
        }
    return ticker_chain_to_calls


def format_calls(ticker_chain_to_calls: dict[(str, str), list[CoinCall]]) -> str:
    sorted_tickers = sorted(
        ticker_chain_to_calls.items(),
        key=lambda kv: max([call.fdv for call in kv[1]]),
        reverse=True,
    )
    res = ""
    for (ticker, chain), calls in sorted_tickers:
        # TODO: don't show chain if none. show ca as well
        ca = calls[0].ca
        res += f"{ticker} ({chain}) - {ca}\n" if chain else f"{ticker} - {ca}\n"
        res += f"{tabulate([coincall_to_row(call) for call in calls])}\n"
        res += "\n"
    return res


def group_into_parts(raw_msg: str, max_len: int) -> list[str]:
    """groups a message into maxlen-length parts, honoring newlines"""
    parts = raw_msg.split("\n\n")
    if len(parts) == 0:
        return []

    current_part = parts[0]
    ret = []
    for part in parts[1:]:
        if len(current_part) + len(part) + 2 <= max_len:
            if len(current_part) > 0:
                current_part += "\n\n" + part
            else:
                current_part = part

        elif len(current_part) > max_len:
            ret.extend(
                [
                    current_part[i : i + max_len]
                    for i in range(0, len(current_part), max_len)
                ]
            )

        else:
            ret.append(current_part)
            current_part = part

    if len(current_part) > max_len:
        ret.extend(
            [
                current_part[i : i + max_len]
                for i in range(0, len(current_part), max_len)
            ]
        )

    else:
        ret.append(current_part)

    return ret
