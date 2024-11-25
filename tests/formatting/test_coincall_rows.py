from datetime import datetime

from trenchview.custom_types import CoinCall
from trenchview.formatting import DT_FORMAT, coincall_to_row, format_dt, row_to_coincall


def test_coincall_to_row_to_coincall():
    # just do a couple examples back and forth
    dt = datetime.strptime("2024-01-01 10:10:10", DT_FORMAT)
    c1 = CoinCall(caller="u1", ticker="ticker", chain="ethereum", fdv=1230, dt=dt)

    r1 = coincall_to_row(c1)
    assert r1 == ["u1", "ticker", "ethereum", "1,230.00", format_dt(dt)]

    assert row_to_coincall(r1) == c1
