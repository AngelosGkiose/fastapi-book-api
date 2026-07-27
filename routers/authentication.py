from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from dependencies.db import get_db
from logger import logger
from models import UserModel
from schemas.users import (
    TokenResponse,
    UserCreate,
    UserResponse
)
from security import (
    create_access_token,
    hash_password,
    verify_password
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def authenticate_user(
    username: str,
    password: str,
    db: Session
) -> UserModel | None:
    user = (
        db.query(UserModel)
        .filter(UserModel.username == username)
        .first()
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user.hashed_password
    ):
        return None

    return user


@router.post(
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
        logger.warning(
            "Registration failed: username already exists: %s",
            user.username
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    existing_email = (
        db.query(UserModel)
        .filter(UserModel.email == user.email)
        .first()
    )

    if existing_email is not None:
        logger.warning(
            "Registration failed: email already exists"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
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

    logger.info(
        "User registered: user_id=%s username=%s",
        new_user.id,
        new_user.username
    )

    return new_user


@router.post(
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
        logger.warning(
            "Failed login attempt: username=%s",
            form_data.username
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        data={
            "sub": user.username
        }
    )

    logger.info(
        "User logged in: user_id=%s username=%s",
        user.id,
        user.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }