from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from exception_handlers import (
    http_exception_handler,
    validation_exception_handler
)
from routers import (
    authentication,
    books,
    categories,
    users
)


app = FastAPI(
    title="Book Management API",
    version="1.0.0"
)


app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)


app.include_router(authentication.router)
app.include_router(books.router)
app.include_router(categories.router)
app.include_router(users.router)


@app.get(
    "/",
    tags=["Root"]
)
def root():
    return {
        "message": "Book Management API is running"
    }