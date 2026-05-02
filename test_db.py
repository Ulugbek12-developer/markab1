import asyncio
from database import search_ads

async def t():
    res = await search_ads('iPhone 12', 'Malika')
    print([dict(r) for r in res])

asyncio.run(t())
