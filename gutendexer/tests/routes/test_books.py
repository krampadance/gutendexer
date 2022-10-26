import json
import pytest
from gutendexer.Config import Config
from gutendexer.schemas.review import ReviewCreate


@pytest.mark.asyncio
async def test_add_review(client):
    """
    Test adding a review
    """
    data = ReviewCreate(rating=5, review="A review")
    response = await client.post("/books/10/review/", data=json.dumps(data.dict()))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_book(client, aioresponses):
    """
    Tests getting a book from the database
    """
    ratings = {
        1: 2.5,
        2: 3,
        3: 2
    }
    reviews_lengths = {
        1: 2,
        2: 1,
        3: 3
    }
    for id in range(1, 3):
        payload = {
            "id": id,
            "title": "test",
            "languages": ["en"],
            "download_count": 10,
            "authors": [{
                "name": "author",
                "birth_year": 1987,
                "death_year": None
            }]
        }
        aioresponses.get("{}/{}".format(Config.GUTENDEX_URL, id),
                         status=200, payload=payload)
        response = await client.get(url="/books/{}/".format(id))
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payload["id"]
        assert data["title"] == payload["title"]
        assert data["languages"] == payload["languages"]
        assert data["download_count"] == payload["download_count"]
        assert len(data["authors"]) == len(payload["authors"])
        assert data["authors"][0]["name"] == payload["authors"][0]["name"]
        assert data["authors"][0]["birth_year"] == payload["authors"][0]["birth_year"]
        assert data["authors"][0]["death_year"] == payload["authors"][0]["death_year"]
        # Assert that average rating is correct
        assert data["rating"] == ratings[id]
        assert len(data["reviews"]) == reviews_lengths[id]


@pytest.mark.asyncio
async def test_get_book_gutendex_exception(client, aioresponses):
    id = 100
    aioresponses.get("{}/{}".format(Config.GUTENDEX_URL, id),
                     status=400, payload={"detail": "Not found."})

    response = await client.get(url="/books/{}/".format(id))
    assert response.status_code == 500
    assert response.json()[
        "detail"] == "Could not fetch data from Gutendex: Not found."


@pytest.mark.asyncio
async def test_search_book(client, aioresponses):
    """
    Tests getting a book from the database
    """
    title = "A book title"

    payload1 = {
        "count": 3,
        "next": "{}?search={}&page=2".format(Config.GUTENDEX_URL, title),
        "previous": None,
        "results": [
            {
                "id":  1,
                "title": "A book with title",
                "languages": ["en"],
                "download_count": 10,
                "authors": [{
                    "name": "author",
                    "birth_year": 1987,
                    "death_year": None
                }]
            },
            {
                "id":  2,
                "title": "No remorse",
                "languages": ["en"],
                "download_count": 10,
                "authors": [{
                    "name": "Book",  # It should be filtered out
                    "birth_year": 1987,
                    "death_year": None
                }]
            }
        ]
    }
    aioresponses.get("{}?search={}".format(Config.GUTENDEX_URL, title),
                     status=200, payload=payload1)
    payload2 = {
        "count": 3,
        "next": None,
        "previous": "{}?search={}".format(Config.GUTENDEX_URL, id, title),
        "results": [
            {
                "id":  3,
                "title": "A book title",
                "languages": ["en"],
                "download_count": 10,
                "authors": [{
                    "name": "author",
                    "birth_year": 1987,
                    "death_year": None
                }]
            }
        ]
    }
    aioresponses.get("{}?search={}&page=2".format(Config.GUTENDEX_URL, title),
                     status=200, payload=payload2)
    response = await client.get(url="/books/search/?title={}".format(title))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 3
