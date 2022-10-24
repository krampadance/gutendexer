from fastapi import HTTPException
import aiohttp
from typing import Union
from motor.motor_tornado import MotorClientSession
from ..schemas.review import Review, ReviewCreate
from ..schemas.book import Book
from ..Config import Config
from .utils import get_book_reviews_pipeline


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
        async with aiohttpSession.get(Config.GUTENDEX_URL, params={"ids": bookId}) as res:
            if res.status != 200:
                raise "exception"
            res_data = await res.json()
    except:
        raise HTTPException(
            status_code=500, detail="Could not fetch data from Gutendex")
    book_data = res_data["results"][0]
    return Book(**review_obj, **book_data)


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
    except:
        raise HTTPException(status_code=500, detail="Could not add review")
