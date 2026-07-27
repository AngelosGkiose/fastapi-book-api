
from fastapi import FastAPI,HTTPException,status, Depends,Query
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import BookModel, CategoryModel, UserModel
from sqlalchemy import or_

from security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    username = payload.get("sub")

    if username is None:
        raise credentials_exception

    user = (
        db.query(UserModel)
        .filter(UserModel.username == username)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user

def get_current_admin(
    current_user: UserModel = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    pages: int = Field(gt=0, le=10000)
    category_id: int = Field(gt=0)
    published_year:int = Field(gt=0)

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    pages: int
    category_id: int
    category: CategoryResponse

    model_config = {
        "from_attributes": True
    }
class CategoryCreate(BaseModel):
    name: str


@app.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    existing_category = (
        db.query(CategoryModel)
        .filter(CategoryModel.name == category.name)
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )

    new_category = CategoryModel(
        name=category.name
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@app.get("/categories",response_model=list[CategoryResponse],status_code=status.HTTP_200_OK)
def get_categories(skip: int = 0,limit: int = 100,db: Session = Depends(get_db)):
    categories=db.query(CategoryModel).offset(skip).limit(limit).all()
    return categories

@app.post(
    "/books",
    status_code=status.HTTP_201_CREATED,
    response_model=BookResponse
)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    category = (
        db.query(CategoryModel)
        .filter(CategoryModel.id == book.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    new_book = BookModel(
        title=book.title,
        author=book.author,
        pages=book.pages,
        category_id=book.category_id,
        published_year=book.published_year
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

@app.put(
    "/books/{book_id}",
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

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    category = (
        db.query(CategoryModel)
        .filter(CategoryModel.id == updated_book.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    book.title = updated_book.title
    book.author = updated_book.author
    book.pages = updated_book.pages
    book.category_id = updated_book.category_id
    book.published_year=updated_book.published_year

    db.commit()
    db.refresh(book)

    return book

@app.delete(
    "/books/{book_id}",
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

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

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

@app.get("/books/category/{category_name}",response_model=list[BookResponse],status_code=status.HTTP_200_OK)
def get_books_by_category(category_name: str,db: Session = Depends(get_db)):
    books=db.query(BookModel).join(CategoryModel).filter(CategoryModel.name==category_name).all()
    return books
@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_username = (
        db.query(UserModel)
        .filter(UserModel.username == user.username)
        .first()
    )

    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists."
        )

    existing_email = (
        db.query(UserModel)
        .filter(UserModel.email == user.email)
        .first()
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists."
        )

    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
def authenticate_user(
        username: str,
        password: str,
        db: Session
):
    user = (
        db.query(UserModel)
        .filter(UserModel.username == username)
        .first()
    )

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
@app.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
        db=db
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={
            "sub": user.username
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@app.get(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_logged_in_user(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user