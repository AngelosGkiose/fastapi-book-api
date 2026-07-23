
from fastapi import FastAPI,HTTPException,status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import BookModel

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

app = FastAPI()
class BookCreate(BaseModel):
    title: str
    author: str
    pages: int


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    pages: int

    model_config = {
        "from_attributes": True
    }


@app.post("/books",status_code=status.HTTP_201_CREATED, response_model=BookResponse)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    new_book = BookModel(
        title=book.title,
        author=book.author,
        pages=book.pages
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@app.put("/books/{book_id}",response_model=BookResponse)
def update_book(book_id: int, updated_book: BookCreate,db: Session = Depends(get_db)):
    book=db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    book.title = updated_book.title
    book.author = updated_book.author
    book.pages = updated_book.pages
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int,db: Session = Depends(get_db)):
    book=db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    db.delete(book)
    db.commit()
    return

@app.get("/books",response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    books=db.query(BookModel).all()
    return books

@app.get(
    "/books/{book_id}",response_model=BookResponse)
def get_book_by_id(
    book_id: int,
    db: Session = Depends(get_db)
):
    book = (
        db.query(BookModel)
        .filter(BookModel.id == book_id)
        .first()
    )

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book