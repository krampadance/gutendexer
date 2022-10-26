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
    for id in range(1, 4):
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
    Tests searching a book title from gutendex
    """
    title = "A book title"

    payload1 = {
        "count": 3,
        "next": "{}/?search={}&page=2".format(Config.GUTENDEX_URL, title),
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
    aioresponses.get("{}/?search={}".format(Config.GUTENDEX_URL, title),
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
    aioresponses.get("{}/?search={}&page=2".format(Config.GUTENDEX_URL, title),
                     status=200, payload=payload2)
    response = await client.get(url="/books/search/?title={}".format(title))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 3


@pytest.mark.asyncio
async def test_search_book_gutendex_exception(client, aioresponses):
    """
    Test searching a book title from gutendex but getting an error response from it.
    """
    title = "Exception title"
    aioresponses.get("{}/?search={}".format(Config.GUTENDEX_URL, title),
                     status=400, payload={"detail": "Not found."})

    response = await client.get(url="/books/search/?title={}".format(title))
    assert response.status_code == 500
    assert response.json()[
        "detail"] == "Could not fetch data from Gutendex: Not found."


@pytest.mark.asyncio
async def test_search_book_paginated(client, aioresponses):
    """
    Tests searching a book using pagination
    """
    title = "A book title"

    payload = {
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
                    "name": "Book",  # It is not filtered out
                    "birth_year": 1987,
                    "death_year": None
                }]
            }
        ]
    }
    aioresponses.get("{}?search={}&page=1".format(Config.GUTENDEX_URL, title),
                     status=200, payload=payload)

    response = await client.get(url="/books/search-paginated/?title={}".format(title))
    assert response.status_code == 200
    data = response.json()
    assert data["totalCount"] == 3
    assert data["page"] == 1
    assert data["totalPages"] == 2
    assert data["nextPage"] == 2
    assert data["previousPage"] == None
    assert len(data["books"]) == 2
    assert data["books"][0]["id"] == 1
    assert data["books"][1]["id"] == 2

    payload = {
        "count": 3,
        "next": None,
        "previous": "{}?search={}&page=1".format(Config.GUTENDEX_URL, title),
        "results": [
            {
                "id":  3,
                "title": "A book with title",
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
                     status=200, payload=payload)

    response = await client.get(url="/books/search-paginated/?title={}&page=2".format(title))
    assert response.status_code == 200
    data = response.json()
    assert data["totalCount"] == 3
    assert data["page"] == 2
    assert data["totalPages"] == 2
    assert data["nextPage"] == None
    assert data["previousPage"] == 1
    assert len(data["books"]) == 1
    assert data["books"][0]["id"] == 3


# TODO: add test for the validation of the page value


@pytest.mark.asyncio
async def test_top_books_by_ratings(client, aioresponses):
    """
    Tests getting a book from the database
    """
    ratings = {
        1: 2.5,
        2: 3,
        3: 2,
        10: 5
    }
    reviews_lengths = {
        1: 2,
        2: 1,
        3: 3,
        10: 1
    }
    for id in range(1, 4):  # Prepare the mocked gutendex responses
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

    payload = {
        "id": 10,
        "title": "test",
        "languages": ["en"],
        "download_count": 10,
        "authors": [{
            "name": "author",
            "birth_year": 1987,
            "death_year": None
        }]
    }
    aioresponses.get("{}/{}".format(Config.GUTENDEX_URL, 10),
                     status=200, payload=payload)

    # Gets top 10 since amount is 10 by default
    response = await client.get(url="/books/top/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4  # We only have reviewed 4 books
    assert data[0]["id"] == 10
    assert data[0]["rating"] == 5
    assert data[1]["id"] == 2
    assert data[1]["rating"] == 3
    assert data[2]["id"] == 1
    assert data[2]["rating"] == 2.5
    assert data[3]["id"] == 3
    assert data[3]["rating"] == 2

    # Reset the mocked responses for gutendex
    for id in range(1, 4):  # Prepare the mocked gutendex responses
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

    payload = {
        "id": 10,
        "title": "test",
        "languages": ["en"],
        "download_count": 10,
        "authors": [{
            "name": "author",
            "birth_year": 1987,
            "death_year": None
        }]
    }
    aioresponses.get("{}/{}".format(Config.GUTENDEX_URL, 10),
                     status=200, payload=payload)

    response = await client.get(url="/books/top/?amount=2")
    data = response.json()
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 10
    assert data[0]["rating"] == 5
    assert data[1]["id"] == 2
    assert data[1]["rating"] == 3
