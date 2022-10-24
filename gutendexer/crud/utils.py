
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
