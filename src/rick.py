
# TODO: types for rick bot

# NOTE: from_user seems broken, so doin ga filter instead
async def get_rick_msgs(client, group, prev_time):
    msgs = await client.get_messages(
        group, 
        reverse=True, # necessary for offset_date to be min_date
        offset_date=prev_time,
        max_id=0, 
        min_id=0
    )

    rick = await client.get_entity("RickBurpBot")
    rick_msgs = [msg for msg in msgs if msg.from_id.user_id == rick.id]

    return rick_msgs

def is_price_check(rick_msg):
    num_lines = len(rick_msg.message.splitlines())
    return num_lines >= 10

