from fastapi import HTTPException
import aiohttp
from typing import Union, List
from motor.motor_tornado import MotorClientSession
from ..schemas.review import Review, ReviewCreate
from ..schemas.book import AverageMonthlyRating, Book, BookAverageMonthlyRating, BookBase, PaginatedBookList
from ..Config import Config
from .utils import filter_title, get_book_reviews_pipeline, get_books, get_top_book_pipeline, get_book_month_average_pipeline
from math import ceil


async def get_book_info(bookId: int, mongoSession: MotorClientSession, aiohttpSession: aiohttp.ClientSession) -> Book:
    """
    Collects the book info from Gutendex and enriches it with review information from mongo.
    """
    collection = mongoSession.client.gutendexer.reviews
    review_obj = {}
    # Collect the reviews for the specific bookId in mongo
    async for agg in collection.aggregate(get_book_reviews_pipeline(
            bookId=bookId), session=mongoSession):
        review_obj = agg
    # Get the book info from gutendex
    try:
        async with aiohttpSession.get("{}/{}".format(Config.GUTENDEX_URL, agg["bookId"])) as res:
            if res.status != 200:
                d = await res.json()
                raise Exception(d["detail"])
            book_data = await res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Could not fetch data from Gutendex: {}".format(e))
    return Book(**review_obj, **book_data)


async def get_book_monthly_average_ratings(bookId: int, mongoSession: MotorClientSession) -> BookAverageMonthlyRating:
    """
    Computes the monthly average ratings of a book in the mongo db
    """
    collection = mongoSession.client.gutendexer.reviews
    monthly_averages = []
    # Collect the monthly average rating for the specific bookId in mongo
    async for agg in collection.aggregate(get_book_month_average_pipeline(
            bookId=bookId), session=mongoSession):
        monthly_averages.append(AverageMonthlyRating(**agg))
    return BookAverageMonthlyRating(bookId=bookId, monthlyAverages=monthly_averages)


async def get_top_books_by_rating(amount: int, mongoSession: MotorClientSession, aiohttpSession: aiohttp.ClientSession) -> List[Book]:
    """
    Computes the top n books based on rating and collects the book info from Gutendex.
    """
    collection = mongoSession.client.gutendexer.reviews
    result = []
    # Collect the reviews for the top books in mongo
    async for agg in collection.aggregate(get_top_book_pipeline(
            amount=amount), session=mongoSession):
        # Get the book info from gutendex
        try:
            async with aiohttpSession.get("{}/{}".format(Config.GUTENDEX_URL, agg["bookId"])) as res:
                if res.status != 200:
                    raise "exception"
                book_data = await res.json()
                result.append(Book(**agg, **book_data))
        except:
            raise HTTPException(
                status_code=500, detail="Could not fetch data from Gutendex")
    return result


async def add_review(bookId: int, review: ReviewCreate, mongoSession: MotorClientSession):
    """
    Inserts a review to the mongo databae
    """
    collection = mongoSession.client.gutendexer.reviews
    try:
        review_obj = Review(**review.dict(), bookId=bookId)
        await collection.insert_one(review_obj.dict(), session=mongoSession)
        return "ok"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not add review")


async def get_books_by_title(title: str, aiohttpSession: aiohttp.ClientSession) -> List[BookBase]:
    """
    Searches the books from Gutendex based on title.
    """
    next = "{}?search={}".format(Config.GUTENDEX_URL, title)
    result = []
    while next is not None:  # Need to get all the books based on gutendex pagination
        books, next = await get_books(url=next, aiohttpSession=aiohttpSession)
        result += [BookBase(**book_data) for book_data in books if filter_title(
            title=book_data["title"], search_string=title)]
    return result


async def get_books_by_title_paginated(title: str, page: int, aiohttpSession: aiohttp.ClientSession) -> PaginatedBookList:
    """
    Searches the books from Gutendex based on title, but uses the pagination.
    For simplicity and to make a paginated solution fast I do not filter on
    the results titles, because, it would mess up with the results take from
    gutendex.
    """
    if page <= 0:
        raise HTTPException(
            status_code=400, detail="Page index should be greater than 0")
    try:
        async with aiohttpSession.get(Config.GUTENDEX_URL, params={"page": page, "search": title}) as res:
            if res.status != 200:
                d = await res.json()
                raise Exception(d["detail"])
            data = await res.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Could not fetch data from Gutendex: {}".format(e))

    next_page = page + 1 if data["next"] is not None else None
    prev_page = page - 1 if data["previous"] is not None else None
    # In the last page the results might be fewer than normally, so that could lead to miscalculation
    total_pages = page if next_page is None else ceil(
        data["count"] / len(data["results"]))
    return PaginatedBookList(
        totalCount=data["count"],
        page=page,
        nextPage=next_page,
        previousPage=prev_page,
        totalPages=total_pages,
        books=[BookBase(**book) for book in data["results"]]
    )
