
from fastapi import FastAPI,HTTPException,status, Depends,Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import BookModel
from sqlalchemy import or_

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

@app.get("/books/search",response_model=BookResponse)
def search_books(title:str,author: str,db: Session = Depends(get_db)):
    book=db.query(BookModel).filter(BookModel.title == title,BookModel.author==author).first()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@app.get("/books/search",response_model=list[BookResponse],status_code=status.HTTP_200_OK)
def search_books_by_title(title:str,author: str,db: Session = Depends(get_db)):
    books=db.query(BookModel).filter(or_(BookModel.title == title,BookModel.author==author)).all()
    return books

@app.get("/books",response_model=list[BookResponse],status_code=status.HTTP_200_OK)
def get_books_sorted(db: Session = Depends(get_db)):
    books=db.query(BookModel).order_by(BookModel.title).all()
    return books

@app.get("/books", response_model=list[BookResponse])
def get_books(
    sort: str = "title",
    order: str = "asc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    if sort == "title":
        sort_column = BookModel.title
    elif sort == "pages":
        sort_column = BookModel.pages
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort parameter"
        )
    if order == "asc":
        order_column = sort_column.asc()
    elif order == "desc":
        order_column = sort_column.desc()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order parameter"
        )
    books = (
        db.query(BookModel).order_by(order_column).offset(skip).limit(limit).all())
    return books

@app.get("/books/filter", response_model=list[BookResponse],status_code=status.HTTP_200_OK)
def filter_books(title: str | None = None,author: str | None = None,min_pages: int | None = None,db: Session = Depends(get_db)):
    query = db.query(BookModel)
    if title:
        query = query.filter(BookModel.title.like(f"%{title}%"))
    if author:
        query = query.filter(BookModel.author.like(f"%{author}%"))
    if min_pages is not None:
        query = query.filter(BookModel.pages >= min_pages)
    books=query.all()
    return books