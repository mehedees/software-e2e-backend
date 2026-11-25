from app.apps.api_service.core.router import APIRouter

from .views import ApplicationStatusViews

common_router = APIRouter()

common_router.add_api_route(
    methods=["GET"],
    path="/livez",
    endpoint=ApplicationStatusViews.live,
    include_in_schema=True,
    name="livez",
    description="Application liveliness status",
    tags=["application status"],
)

common_router.add_api_route(
    methods=["GET"],
    path="/readyz",
    endpoint=ApplicationStatusViews.ready,
    include_in_schema=True,
    name="readyz",
    description="Application readiness status",
    tags=["application status"],
)
