from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.apps.api_service.core.errors.api_exception import APIException
from app.apps.api_service.core.schema.response import APIErrorResponse, ErrorDetail


def _status_name(status_code: int) -> str:
    """`404` -> `"NOT_FOUND"`; falls back to `"HTTP_<code>"` for non-standard codes."""
    try:
        return HTTPStatus(status_code).name
    except ValueError:
        return f"HTTP_{status_code}"


def _status_phrase(status_code: int) -> str:
    """`404` -> `"Not Found"`; falls back to `"HTTP <code>"` for non-standard codes."""
    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return f"HTTP {status_code}"


def _error_response(
    status_code: int,
    body: APIErrorResponse,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=body.model_dump(), headers=headers
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return 422 validation errors as an `APIErrorResponse`.

    Only `loc`, `msg` and `type` are kept from Pydantic's errors; `input` is
    dropped so user-submitted values (e.g. passwords) are never echoed back.
    """
    errors = [
        ErrorDetail(
            field=".".join(str(part) for part in error["loc"]),
            message=error["msg"],
            code=error["type"],
        )
        for error in exc.errors()
    ]
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        APIErrorResponse(
            code="VALIDATION_ERROR", message="Invalid request", errors=errors
        ),
    )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Return an `APIException` raised by an endpoint as an `APIErrorResponse`."""
    return _error_response(
        exc.status_code,
        APIErrorResponse(
            code=exc.code,
            message=exc.message or _status_phrase(exc.status_code),
            errors=exc.errors,
        ),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Return `HTTPException`s (incl. routing 404/405) as an `APIErrorResponse`.

    Registered on Starlette's class so it also catches FastAPI's subclass and
    the router's own 404/405. Headers (e.g. `Allow`, `WWW-Authenticate`) are kept.
    """
    message = exc.detail if isinstance(exc.detail, str) else None
    return _error_response(
        exc.status_code,
        APIErrorResponse(
            code=_status_name(exc.status_code),
            message=message or _status_phrase(exc.status_code),
        ),
        headers=exc.headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return any uncaught exception as a 500 `APIErrorResponse`.

    No exception details are sent to the client; Starlette's
    `ServerErrorMiddleware` still re-raises it afterwards so it gets logged.
    """
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        APIErrorResponse(
            code="INTERNAL_ERROR",
            message=_status_phrase(status.HTTP_500_INTERNAL_SERVER_ERROR),
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
