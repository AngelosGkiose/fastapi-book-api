from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies.authentication import (
    get_current_admin,
    get_current_user
)
from dependencies.db import get_db
from models import UserModel
from schemas.users import (
    UserResponse,
    UserRoleUpdate
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse
)
def get_logged_in_user(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse
)
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.role = role_update.role

    db.commit()
    db.refresh(user)

    return user