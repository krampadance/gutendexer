from pydantic import BaseModel
from typing import Optional, List


class Author(BaseModel):
    name: str
    birth_year: Optional[int] = None
    death_year: Optional[int] = None


class BookBase(BaseModel):
    id: int
    title: str
    authors: List[Author]
    languages: List[str]
    download_count: int


class Book(BookBase):
    rating: Optional[float] = None
    reviews: Optional[List[str]]


class AverageMonthlyRating(BaseModel):
    month: int
    year: int
    rating: float


class BookAverageMonthlyRating(BaseModel):
    bookId: int
    monthlyAverages: List[AverageMonthlyRating]


class PaginatedBookList(BaseModel):
    totalCount: int
    page: int
    totalPages: int
    nextPage: Optional[int] = None
    previousPage: Optional[int] = None
    books: List[BookBase]
