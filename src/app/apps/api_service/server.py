from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from app.libs.settings import CommonSettings, get_common_settings

from .core.errors.api_exception import APIException
from .core.errors.exception_handlers import (
    api_exception_handler,
    common_http_exception_handler,
    request_validation_error_handler,
    unhandled_exception_handler,
)
from .core.middlewares.context import RequestContextMiddleware
from .core.middlewares.request_id import (
    REQUEST_ID_HEADER,
    TRACE_ID_HEADER,
    RequestIDMiddleware,
)
from .core.schema.response import FirewallError, InternalServerError
from .core.settings import APISettings, get_settings


@asynccontextmanager
async def lifespan(_main_app: FastAPI) -> AsyncIterator[None]:
    """
    Startup and shutdown event handler for the "main" fastapi app.
    Lifespan only runs once for the main app. Sub-apps don't own/run their own lifespan even if lifespan is passed.
    """
    yield


def register_common_exception_handlers(fastapi_app: FastAPI) -> None:
    # only applicable for this particular app, no global wrapping
    fastapi_app.add_exception_handler(
        RequestValidationError, request_validation_error_handler
    )
    fastapi_app.add_exception_handler(APIException, api_exception_handler)
    fastapi_app.add_exception_handler(
        StarletteHTTPException, common_http_exception_handler
    )
    fastapi_app.add_exception_handler(Exception, unhandled_exception_handler)


def register_global_middlewares(fastapi_app: FastAPI, settings: APISettings) -> None:
    """Add the global middlewares. Wraps the main app and sub-apps.

    `add_middleware` wraps the app, so the middleware added last is the
    outermost and runs first on each request. Add new middlewares above
    `RequestContextMiddleware` so it stays outermost and they can all read the
    request context.
    """
    fastapi_app.add_middleware(  # after RequestIDMiddleware, so CORS preflight responses still get ids
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        max_age=settings.CORS_MAX_AGE,
        # Let browser code read the ids `RequestIDMiddleware` sets.
        expose_headers=[REQUEST_ID_HEADER, TRACE_ID_HEADER],
    )
    fastapi_app.add_middleware(RequestIDMiddleware)
    fastapi_app.add_middleware(RequestContextMiddleware)  # keep at the bottom


COMMON_RESPONSES = {
    403: {"model": FirewallError, "description": "Blocked by firewall"},
    500: {"model": InternalServerError, "description": "Internal Server Error"},
}


def create_app(api_settings: APISettings, common_settings: CommonSettings) -> FastAPI:
    root_app = FastAPI(
        debug=common_settings.DEBUG,
        lifespan=lifespan,
        title=api_settings.TITLE,
        summary=api_settings.SUMMARY,
        description=api_settings.DESCRIPTION,
        version=common_settings.PROJECT_VERSION,
        openapi_url=api_settings.OPENAPI_URL,
        responses=COMMON_RESPONSES,
    )

    # setup root app
    register_global_middlewares(root_app, api_settings)
    register_common_exception_handlers(root_app)

    # create sub apps
    portal_app = FastAPI(
        debug=common_settings.DEBUG,
        openapi_url=api_settings.OPENAPI_URL,
        responses=COMMON_RESPONSES,
    )
    mobile_app = FastAPI(
        debug=common_settings.DEBUG,
        openapi_url=api_settings.OPENAPI_URL,
        responses=COMMON_RESPONSES,
    )

    # mount apps
    root_app.mount(APISettings.PORTAL_API_URL_PREFIX, portal_app)
    root_app.mount(APISettings.MOBILE_API_URL_PREFIX, mobile_app)

    # register common exception handlers for each sub-app
    register_common_exception_handlers(portal_app)
    register_common_exception_handlers(mobile_app)

    # register routes
    from .core.register_routers import (
        register_mobile_app_routers,
        register_portal_app_routers,
        register_root_app_routers,
    )

    register_root_app_routers(root_app)
    register_portal_app_routers(portal_app)
    register_mobile_app_routers(mobile_app)

    return root_app


app: FastAPI = create_app(
    api_settings=get_settings(), common_settings=get_common_settings()
)
