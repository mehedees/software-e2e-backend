from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.apps.api_service.core.middlewares.context import RequestContextMiddleware
from app.apps.api_service.core.middlewares.request_id import (
    REQUEST_ID_HEADER,
    TRACE_ID_HEADER,
    RequestIDMiddleware,
)
from app.apps.api_service.core.settings import CORSSettings


def register_middlewares(app: FastAPI) -> None:
    """Add the app's middlewares.

    `add_middleware` wraps the app, so the middleware added last is the
    outermost and runs first on each request. Add new middlewares above
    `RequestContextMiddleware` so it stays outermost and they can all read the
    request context.
    """
    _add_cors(app)  # innermost, so CORS preflight responses still get ids
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestContextMiddleware)  # keep at the bottom


def _add_cors(app: FastAPI) -> None:
    settings = CORSSettings()
    if not settings.allow_origins:
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_methods=settings.allow_methods,
        allow_headers=settings.allow_headers,
        allow_credentials=settings.allow_credentials,
        max_age=settings.max_age,
        # Let browser code read the ids `RequestIDMiddleware` sets.
        expose_headers=[REQUEST_ID_HEADER, TRACE_ID_HEADER],
    )
