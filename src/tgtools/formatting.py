from datetime import datetime
from pprint import pprint

import pytz
from tabulate import tabulate

from tgtools.types import CoinCall

TABLE_ROW_HEADERS = ["caller", "ticker", "call-fdv ($)", "dt"]


DT_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_dt(dt: datetime):
    local_tz = pytz.timezone("America/Los_Angeles")
    local_dt = dt.astimezone(local_tz)

    return local_dt.strftime(DT_FORMAT)


# NOTE: change this and the method below in lock step! might be worth writing a test...
def coincall_to_row(call: CoinCall) -> list[str]:
    return [call.caller, call.ticker, f"{call.call_fdv:,.2f}", format_dt(call.dt)]


def row_to_coincall(row: list[str]) -> CoinCall:
    return CoinCall(
        row[0],
        row[1],
        float(row[2].replace(",", "")),
        datetime.strptime(row[3], DT_FORMAT),
    )


def format_coin_calls(coin_calls: list[CoinCall]) -> str:
    """Default tabulation method used in tgtools"""

    fdv_sorted_calls = sorted(
        coin_calls,
        key=lambda x: x.call_fdv,
        reverse=True,
    )

    table_rows = [coincall_to_row(call) for call in fdv_sorted_calls]

    return tabulate(table_rows, headers=TABLE_ROW_HEADERS)


def discover_and_print(obj, depth=5):
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
