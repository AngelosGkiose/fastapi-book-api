
from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel

app = FastAPI()
class Book(BaseModel):
    id: int
    title: str
    author: str
    pages: int


books = []


@app.post(
    "/books",
    status_code=status.HTTP_201_CREATED,
    response_model=Book
)
def create_book(book: Book):
    books.append(book)
    return book


@app.put(
    "/books/{book_id}",
    response_model=Book
)
def update_book(book_id: int, updated_book: Book):
    for index, book in enumerate(books):
        if book.id == book_id:
            books[index] = updated_book
            return updated_book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found"
    )

@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    for index,book in enumerate(books):
        if book.id==book_id :
            books.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")

@app.get("/books",response_model=list[Book])
def get_books():
    return books