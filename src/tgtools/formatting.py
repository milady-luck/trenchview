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
    # sort by ath_fdv, then call_fdv, reversed
    # tabulate?

    fdv_sorted_calls = sorted(
        coin_calls,
        key=lambda x: (x.parsed_resp.ath_fdv, x.parsed_resp.call_fdv),
        reverse=True,
    )

    table_rows = [extract_table_row(call) for call in fdv_sorted_calls]

    return tabulate(table_rows, headers=TABLE_ROW_HEADERS)
