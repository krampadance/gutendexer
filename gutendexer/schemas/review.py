import datetime
from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReviewBase(BaseModel):
    rating: int
    review: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class Review(ReviewBase):
    bookId: int
    createdAt: datetime = datetime.now()
