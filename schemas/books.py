from pydantic import BaseModel, Field

from schemas.categories import CategoryResponse


class BookCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200
    )
    author: str = Field(
        min_length=1,
        max_length=100
    )
    pages: int = Field(
        gt=0,
        le=10000
    )
    published_year: int = Field(
        ge=1000,
        le=2100
    )
    category_id: int = Field(gt=0)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    pages: int
    published_year: int | None
    category_id: int
    category: CategoryResponse

    model_config = {
        "from_attributes": True
    }