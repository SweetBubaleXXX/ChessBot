import asyncio

from . import db

asyncio.run(db.create_table_users)
