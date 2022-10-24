from fastapi import APIRouter, Depends
from motor.motor_tornado import MotorClientSession
import aiohttp
from typing import Union

from ..schemas.book import Book
from .dependencies import get_db_session, get_aiohttp_session
from ..crud.books import get_book_info, add_review
from ..schemas.review import ReviewCreate

router = APIRouter(
    prefix="/books",
    tags=["books"],
)


# @router.get("/", response_model=List[Book])
# def get_all(title: Union[str, None] = None, db: Session = Depends(get_db)):
#     return get_all_books(db=db, title=title)


@router.get("/{bookId}/", response_model=Book)
async def get_book(bookId: int, mongoSession: MotorClientSession = Depends(get_db_session), aiohttpSession: aiohttp.ClientSession = Depends(get_aiohttp_session)):
    return await get_book_info(bookId=bookId, mongoSession=mongoSession, aiohttpSession=aiohttpSession)


@router.post("/{bookId}/review/")
async def review(book_id: int, review: ReviewCreate, mongoSession: MotorClientSession = Depends(get_db_session)):
    return await add_review(bookId=book_id, review=review, mongoSession=mongoSession)
