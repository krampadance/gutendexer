import pytest_asyncio
from ..Config import Config
import motor.motor_asyncio
from fastapi import FastAPI
import pytest
from typing import Generator
from typing import Any
from ..routes import books
from ..routes.dependencies import get_db_session
import asyncio
import sys
import os
from httpx import AsyncClient
from datetime import datetime
import aioresponses as aioresponses_


# this is to include backend dir in sys.path so that we can import from db,main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def start_application():
    app = FastAPI()
    # Add routers to the app
    app.include_router(books.router)
    return app


@pytest.fixture
def aioresponses():
    with aioresponses_.aioresponses() as aior:
        yield aior


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://{}:{}@{}/{}".format(
            Config.MONGO_USER, Config.MONGO_PASSWORD, Config.MONGO_HOST, "gutendexer"))
    db = client.get_default_database()
    collection = client.gutendexer.reviews
    await collection.insert_many([
        {
            "bookId": 1,
            "rating": 0,
            "review": "Review",
            "createdAt": datetime.strptime("01/10/22", '%d/%m/%y')
        },
        {
            "bookId": 1,
            "rating": 5,
            "review": "Review",
            "createdAt": datetime.strptime("02/10/22", '%d/%m/%y')
        },
        {
            "bookId": 2,
            "rating": 3,
            "review": "Review",
            "createdAt": datetime.strptime("02/10/22", '%d/%m/%y')
        },
        {
            "bookId": 3,
            "rating": 1,
            "review": "Review",
            "createdAt": datetime.strptime("02/10/22", '%d/%m/%y')
        },
        {
            "bookId": 3,
            "rating": 2,
            "review": "Review",
            "createdAt": datetime.strptime("02/11/22", '%d/%m/%y')
        },
        {
            "bookId": 3,
            "rating": 3,
            "review": "Review",
            "createdAt": datetime.strptime("02/10/22", '%d/%m/%y')
        }
    ])
    yield None
    await collection.delete_many({})


@pytest_asyncio.fixture(scope="session")
def app() -> Generator[FastAPI, Any, None]:
    _app = start_application()
    yield _app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def mongoSession(event_loop, app: FastAPI) -> Generator[motor.motor_asyncio.AsyncIOMotorClientSession, Any, None]:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://{}:{}@{}/{}".format(
            Config.MONGO_USER, Config.MONGO_PASSWORD, Config.MONGO_HOST, "gutendexer"))
    session = await client.start_session()
    try:
        yield session
    finally:
        session.end_session()


@pytest_asyncio.fixture(scope="session")
async def client(app: FastAPI, mongoSession: motor.motor_asyncio.AsyncIOMotorClientSession) -> Generator:
    def _get_test_db_session():
        try:
            yield mongoSession
        finally:
            pass

    app.dependency_overrides[get_db_session] = _get_test_db_session
    async with AsyncClient(app=app, base_url="http://testserver") as client:

        yield client
