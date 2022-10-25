import datetime
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional


class ReviewBase(BaseModel):
    rating: float
    review: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class Review(ReviewBase):
    bookId: int
    createdAt: datetime = datetime.now()

    @validator('rating')
    def check_rating(cls, v):
        if v > 5 or v < 0:
            raise ValueError('Rating is not between 0 and 5')
        return v
