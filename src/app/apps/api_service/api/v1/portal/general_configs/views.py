from app.apps.api_service.core.schema.response import APIResponse


class GeneralConfigViews:
    @staticmethod
    def list() -> APIResponse[list[dict]]:
        return APIResponse(data=[{"dummy_config_key": "dummy value"}])

    @staticmethod
    def detail(config_key: str) -> APIResponse[dict]:
        return APIResponse(
            data={"key": f"{config_key}", "type": "type", "value": "value"}
        )
