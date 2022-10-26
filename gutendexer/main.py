from fastapi import FastAPI
from .routes import books

app = FastAPI()

app.include_router(books.router)


@app.get("/")
async def root():
    return {"message": "Gutendexer API"}
