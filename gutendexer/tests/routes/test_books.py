import json
import pytest
import pytest_asyncio
from gutendexer.Config import Config
from httpx import AsyncClient
from gutendexer.schemas.review import ReviewCreate


@pytest.mark.asyncio
async def test_add_review(client):
    data = ReviewCreate(rating=5, review="A review")
    response = await client.post("/books/10/review/", data=json.dumps(data.dict()))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_book(client):
    response = await client.get(url="/books/1/")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["rating"] == 2.5
