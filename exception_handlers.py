from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(
    request: Request,
    exception: StarletteHTTPException
):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "success": False,
            "message": exception.detail,
            "errors": None
        },
        headers=exception.headers
    )


async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError
):
    validation_errors = []

    for error in exception.errors():
        field_parts = error["loc"]

        if field_parts and field_parts[0] in {
            "body",
            "query",
            "path"
        }:
            field_parts = field_parts[1:]

        field_location = ".".join(
            str(location)
            for location in field_parts
        )

        validation_errors.append({
            "field": field_location,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": validation_errors
        }
    )