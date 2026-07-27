from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.orm import Session

from dependencies.authentication import get_current_admin
from dependencies.db import get_db
from logger import logger
from models import BookModel, CategoryModel, UserModel
from schemas.books import BookCreate, BookResponse


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.get(
    "",
    response_model=list[BookResponse],
    status_code=status.HTTP_200_OK
)
def get_books(
    title: str | None = None,
    author: str | None = None,
    category: str | None = None,
    min_pages: int | None = Query(
        default=None,
        gt=0
    ),
    published_year: int | None = Query(
        default=None,
        ge=1000,
        le=2100
    ),
    sort: str = Query(
        default="title",
        pattern="^(title|author|pages|published_year)$"
    ),
    order: str = Query(
        default="asc",
        pattern="^(asc|desc)$"
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db)
):
    query = db.query(BookModel)

    if title:
        query = query.filter(
            BookModel.title.ilike(f"%{title}%")
        )

    if author:
        query = query.filter(
            BookModel.author.ilike(f"%{author}%")
        )

    if category:
        query = (
            query
            .join(CategoryModel)
            .filter(
                CategoryModel.name.ilike(
                    f"%{category}%"
                )
            )
        )

    if min_pages is not None:
        query = query.filter(
            BookModel.pages >= min_pages
        )

    if published_year is not None:
        query = query.filter(
            BookModel.published_year == published_year
        )

    sort_columns = {
        "title": BookModel.title,
        "author": BookModel.author,
        "pages": BookModel.pages,
        "published_year": BookModel.published_year
    }

    sort_column = sort_columns[sort]

    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    books = (
        query
        .order_by(sort_column)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return books


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK
)
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


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    category = (
        db.query(CategoryModel)
        .filter(
            CategoryModel.id == book.category_id
        )
        .first()
    )

    if category is None:
        logger.warning(
            "Book creation failed: category_id=%s not found",
            book.category_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    new_book = BookModel(
        title=book.title,
        author=book.author,
        pages=book.pages,
        published_year=book.published_year,
        category_id=book.category_id
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    logger.info(
        "Book created: book_id=%s title=%s admin_id=%s",
        new_book.id,
        new_book.title,
        current_admin.id
    )

    return new_book


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK
)
def update_book(
    book_id: int,
    updated_book: BookCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    book = (
        db.query(BookModel)
        .filter(BookModel.id == book_id)
        .first()
    )

    if book is None:
        logger.warning(
            "Book update failed: book_id=%s not found",
            book_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    category = (
        db.query(CategoryModel)
        .filter(
            CategoryModel.id == updated_book.category_id
        )
        .first()
    )

    if category is None:
        logger.warning(
            "Book update failed: category_id=%s not found",
            updated_book.category_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    book.title = updated_book.title
    book.author = updated_book.author
    book.pages = updated_book.pages
    book.published_year = updated_book.published_year
    book.category_id = updated_book.category_id

    db.commit()
    db.refresh(book)

    logger.info(
        "Book updated: book_id=%s admin_id=%s",
        book.id,
        current_admin.id
    )

    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    book = (
        db.query(BookModel)
        .filter(BookModel.id == book_id)
        .first()
    )

    if book is None:
        logger.warning(
            "Book deletion failed: book_id=%s not found",
            book_id
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    book_title = book.title

    db.delete(book)
    db.commit()

    logger.info(
        "Book deleted: book_id=%s title=%s admin_id=%s",
        book_id,
        book_title,
        current_admin.id
    )