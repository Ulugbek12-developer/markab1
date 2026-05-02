import asyncio
import aiosqlite

async def t():
    db = await aiosqlite.connect('db.sqlite3')
    db.row_factory = aiosqlite.Row
    c = await db.execute('SELECT 1 as id')
    r = await c.fetchall()
    print([dict(x) for x in r])
    await db.close()

asyncio.run(t())
