import aiosqlite

DATABASE_URL = "sqlite_async.db"

async def get_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        yield db

async def execute(query: str, is_many: bool = False, args=[]):
    async with aiosqlite.connect(DATABASE_URL) as db:
        if is_many:
            await db.executemany(query, args)
        else:
            await db.execute(query, args)
        await db.commit()

async def fetch(query: str, args=[]):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(query, args)
        records = await cursor.fetchall()
        return records
