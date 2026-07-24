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