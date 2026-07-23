from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel

app = FastAPI()
class Book(BaseModel):
    id: int
    title: str
    author: str
    pages: int


books = []


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: Book):
    books.append(book)
    return book



@app.put("/books/{book_id}")
def update_book(book_id: int, updated_book: Book):
    for index, book in enumerate(books):
        if book.id == book_id:
            books[index] = updated_book
            return updated_book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
    )