# app/db.py
import asyncio
import asyncpg

DATABASE_URL = "postgresql://username:password@localhost:5432/vortexai"

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def disconnect(self):
        await self.pool.close()

    async def execute(self, query, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch_one(self, query, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def fetch_all(self, query, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

database = Database()
