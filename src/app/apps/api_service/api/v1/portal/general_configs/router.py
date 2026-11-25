from app.apps.api_service.core.router import APIRouter

from .views import GeneralConfigViews

general_config_router = APIRouter()

general_config_router.add_api_route(
    path="/",
    methods=["GET"],
    endpoint=GeneralConfigViews.list,
    name="General Config List",
    description="List all general configs",
)

general_config_router.add_api_route(
    path="/{config_key}",
    methods=["GET"],
    endpoint=GeneralConfigViews.detail,
    name="General Config Detail",
    description="Get a specific general config",
)
