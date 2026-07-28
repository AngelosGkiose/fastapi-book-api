from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from dependencies.authentication import (
    get_current_admin,
    get_current_user
)
from dependencies.db import get_db
from models import CategoryModel, UserModel
from schemas.categories import (
    CategoryCreate,
    CategoryResponse
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    existing_category = (
        db.query(CategoryModel)
        .filter(CategoryModel.name == category.name)
        .first()
    )

    if existing_category is not None:
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


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK
)
def get_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return (
        db.query(CategoryModel)
        .offset(skip)
        .limit(limit)
        .all()
    )