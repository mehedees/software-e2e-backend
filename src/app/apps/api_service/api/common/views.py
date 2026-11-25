from app.apps.api_service.api.common.dto import ReadyStatusResponseData
from app.apps.api_service.core.schema.response import APIResponse, DataEmpty


class ApplicationStatusViews:
    @staticmethod
    async def live() -> APIResponse[DataEmpty]:
        return APIResponse(data=DataEmpty())

    @staticmethod
    async def ready() -> APIResponse[ReadyStatusResponseData]:
        # asyncio.gather dependency statuses
        return APIResponse(data=ReadyStatusResponseData())
