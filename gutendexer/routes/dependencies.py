from typing import Generator
import motor.motor_asyncio
import aiohttp
from ..Config import Config


async def get_db_session() -> Generator:
    """
    Database session/connection to be used per request, it is passed as a dependency to the endpoints
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://{}:{}@{}/{}".format(
            Config.MONGO_USER, Config.MONGO_PASSWORD, Config.MONGO_HOST, Config.DATABASE))
    session = await client.start_session()
    try:
        yield session
    finally:
        session.end_session()


async def get_aiohttp_session() -> Generator:
    """
    aiohttp session to be passed as a dependency to the endpoints.
    It is used to contact gutendex api inside the routes
    """
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()
