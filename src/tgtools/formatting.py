from pprint import pprint

from tabulate import tabulate

from tgtools.types import CoinCall

TABLE_ROW_HEADERS = ["ticker", "call-fdv ($)", "ath-fdv ($)", "caller", "timestamp"]


# TODO: format fdvs
def extract_table_row(call: CoinCall):
    return [
        call.parsed_resp.ticker,
        f"{call.parsed_resp.call_fdv:,.2f}",
        f"{call.parsed_resp.ath_fdv:,.2f}",
        call.caller_username,
        "TODO",  # TODO: timestamp
    ]


def format_coin_calls(coin_calls: list[CoinCall]) -> str:
    """Default tabulation method used in tgtools"""

    fdv_sorted_calls = sorted(
        coin_calls,
        key=lambda x: (x.parsed_resp.ath_fdv, x.parsed_resp.call_fdv),
        reverse=True,
    )

    table_rows = [extract_table_row(call) for call in fdv_sorted_calls]

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
