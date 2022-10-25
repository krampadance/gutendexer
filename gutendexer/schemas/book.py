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
    month: str
    rating: float


class BookAverageMonthlyRating(BaseModel):
    bookId: int
    monthlyAverages: List[AverageMonthlyRating]
