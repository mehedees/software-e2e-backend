from fastapi import status

from app.apps.api_service.core.schema.response import ErrorDetail


class APIException(Exception):  # noqa: N818
    """Raise from an endpoint to return an `APIErrorResponse`.

    The handler in `core.bootstrap.exception_handlers` turns it into a
    `JSONResponse` with `status_code` and body
    `{"code": ..., "message": ..., "errors": [...]}`. If `message` is omitted,
    the standard reason phrase for `status_code` is used.

        raise APIException(status_code=404, code="NOT_FOUND", message="User not found")

        raise APIException(
            status_code=409,
            code="CONFLICT",
            message="Could not create user",
            errors=[ErrorDetail(field="body.email", message="Email already taken")],
        )
    """

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        message: str | None = None,
        errors: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(message or code)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.errors = errors or []
