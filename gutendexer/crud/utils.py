import aiohttp
from fastapi import HTTPException


def get_book_reviews_pipeline(bookId: int):
    """
    Returns the pipeline object that is used for the aggregation
    to get the reviews and average rating of a book,
    """
    return [
        {
            "$match": {"bookId": bookId}
        }, {
            "$group": {
                "_id": "$bookId",
                "rating": {"$avg": "$rating"},
                "reviews": {"$push": "$review"}
            }
        }, {
            "$project": {
                "bookId": "$_id",
                "rating": 1,
                "reviews": 1,
                "_id": 0
            }
        }
    ]


def get_book_month_average_pipeline(bookId: int):
    """
    Returns the pipeline object that is used for the aggregation
    to get average rating of a book per month
    """
    return [
        {
            "$match": {"bookId": bookId}
        }, {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m", "date": "$createdAt"}},
                "rating": {"$avg": "$rating"}
            }
        }, {
            "$project": {
                "rating": 1,
                "_id": 0,
                "month": "$_id"
            }
        }
    ]


def get_top_book_pipeline(amount: int):
    """
    Returns the pipeline object that is used for the aggregation
    to get the reviews and average rating of a book,
    """
    return [
        {
            "$group": {
                "_id": "$bookId",
                "rating": {"$avg": "$rating"},
                "reviews": {"$push": "$review"}
            }
        },
        {
            "$sort": {
                "rating": -1
            }
        },
        {
            "$limit": amount
        },
        {
            "$project": {
                "bookId": "$_id",
                "rating": 1,
                "reviews": 1,
                "_id": 0
            }
        }
    ]


def filter_title(title: str, search_string: str) -> bool:
    """
    We are filtering the title, base on the actual search string
    because gutendex, checks for the search terms either in the 
    title or the author.

    Q(authors__name__icontains=term) | Q(title__icontains=term)

    in line https://github.com/garethbjohnson/gutendex/blob/814a883430eb6fa144e92ac3d14b992963f6291a/books/views.py#L92
    so since we want to search on title we have to filter it.
    """
    for term in search_string.split(" "):
        if term not in title:
            return False
    return True


async def get_books(url, aiohttpSession: aiohttp.ClientSession):
    """
    Returns the book data and the next url, in order to recursively fetch all
    books at once
    """
    try:
        async with aiohttpSession.get(url) as res:
            if res.status != 200:
                raise "exception"
            res_data = await res.json()
            return res_data["results"], res_data["next"]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Could not fetch data from Gutendex")
