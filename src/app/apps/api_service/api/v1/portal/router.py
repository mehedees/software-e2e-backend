from app.apps.api_service.core.router import APIRouter

from .general_configs.router import general_config_router

v1_portal_router = APIRouter()
v1_portal_router.include_router(
    general_config_router, prefix="/general-config", tags=["general configs"]
)
