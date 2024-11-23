from trenchview.parsing import parse_coin_call
from trenchview.tg.scraping import get_recent_rickbot_calls


async def get_recent_tg_calls(tg_client, group_id, prev_time):
    rickbot_calls = await get_recent_rickbot_calls(tg_client, group_id, prev_time)
    coin_calls = [
        c for c in [parse_coin_call(m) for m in rickbot_calls] if c is not None
    ]

    return coin_calls
