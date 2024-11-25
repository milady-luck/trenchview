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


# TODO: fix these when I change CoinCall


# NOTE: change this and the method below in lock step! might be worth writing a test...
def coincall_to_row(call: CoinCall) -> list[str]:
    return [
        call.caller,
        call.ticker,
        call.chain,
        f"{call.fdv:,.2f}",
        format_dt(call.dt),
    ]


def row_to_coincall(row: list[str]) -> CoinCall:
    return CoinCall(
        caller=row[0],
        ticker=row[1],
        chain=row[2],
        fdv=float(row[3].replace(",", "")),
        dt=datetime.strptime(f"{row[4]}", DT_FORMAT),
    )


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


def group_by_ticker(
    calls: list[CoinCall], multi_only=False
) -> dict[str, list[CoinCall]]:
    ticker_to_calls: dict[str, list[CoinCall]] = defaultdict(list)
    for call in calls:
        ticker_to_calls[call.ticker].append(call)

    # sort calls for a given ticker by dt
    ticker_to_calls = {
        ticker: sorted(calls, key=lambda call: call.dt)
        for ticker, calls in ticker_to_calls.items()
    }

    # filter if multicalled only
    if multi_only:
        ticker_to_calls = {
            ticker: calls for ticker, calls in ticker_to_calls.items() if len(calls) > 1
        }
    return ticker_to_calls


def format_ticker_calls(ticker_to_calls: dict[str, list[CoinCall]]) -> str:
    sorted_tickers = sorted(
        ticker_to_calls.items(),
        key=lambda kv: max([call.fdv for call in kv[1]]),
        reverse=True,
    )
    res = ""
    for ticker, calls in sorted_tickers:
        res += f"{ticker}\n"
        res += f"{tabulate([coincall_to_row(call) for call in calls])}\n"
        res += "\n"
    return res
