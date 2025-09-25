"""Exception handler."""
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class CustomError(Exception):
    """Custom error."""

    http_code: int
    success: bool
    message: Optional[str]

    def __init__(
        self,
        http_code: int = 400,
        success: bool = False,
        message: Optional[str] = None,
    ) -> None:
        self.http_code = http_code if http_code else 400
        self.success = success
        self.message = message


async def http_exception_handler(
    request: Request,
    exc: CustomError,
) -> JSONResponse:
    """HTTP error handler."""
    return JSONResponse(
        status_code=exc.http_code,
        content=jsonable_encoder(
            JSONResponse().custom_response(exc.success, exc.message),
        ),
    )


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )