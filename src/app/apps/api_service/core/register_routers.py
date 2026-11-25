from fastapi import FastAPI

from ..api.common.router import common_router
from ..api.v1.mobile.router import v1_mobile_router
from ..api.v1.portal.router import v1_portal_router


def register_root_app_routers(app: FastAPI) -> None:
    app.include_router(common_router, prefix="", tags=["common"])


def register_portal_app_routers(app: FastAPI) -> None:
    app.include_router(v1_portal_router, prefix="/v1", tags=["v1"])


def register_mobile_app_routers(app: FastAPI) -> None:
    app.include_router(v1_mobile_router, prefix="/v1", tags=["v1"])
