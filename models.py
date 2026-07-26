from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class BookModel(Base):
    __tablename__ = "books"
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    title = Column(
        String,
        nullable=False
    )
    author = Column(
        String,
        nullable=False
    )

    pages = Column(
        Integer,
        nullable=False
    )
    published_year = Column(Integer, nullable=True)
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False)
    category = relationship(
        "CategoryModel",
        back_populates="books"
    )

class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    books = relationship(
        "BookModel",
        back_populates="category"
    )

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")