import functools

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.libs.settings import (
    BaseAppSettings,
    CommaSeparatedList,
    DeploymentEnv,
    get_common_settings,
)


class APISettings(BaseAppSettings):
    """Settings only the API service uses, read from `API_*` environment variables.

    Fields are named `<RESPONSIBILITY>_<KEY>` and read from
    `API_<RESPONSIBILITY>_<KEY>`, e.g. `CORS_ALLOW_ORIGINS` from
    `API_CORS_ALLOW_ORIGINS`. Shared settings (MySQL, Redis, ...) live in
    `app.libs.settings.CommonSettings`, not here.

    List values are comma-separated, e.g.
    `API_CORS_ALLOW_ORIGINS=https://app.example.com,http://localhost:3000`.

    Read through `get_settings()`, not by instantiating this class.
    """

    model_config = SettingsConfigDict(env_prefix="API_")

    TITLE: str = "API Service"
    SUMMARY: str = ""
    DESCRIPTION: str = ""
    PORTAL_API_URL_PREFIX: str = "/api/portal"
    MOBILE_API_URL_PREFIX: str = "/api/mobile"
    OPENAPI_URL: str | None = "/openapi.json"

    # With no origins set, CORS is off and browsers block cross-origin calls.
    CORS_ALLOW_ORIGINS: CommaSeparatedList = Field(default_factory=list)
    CORS_ALLOW_METHODS: CommaSeparatedList = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: CommaSeparatedList = Field(default_factory=lambda: ["*"])
    # Don't combine with `API_CORS_ALLOW_ORIGINS=*`: Starlette then echoes any
    # origin back, which lets every site make credentialed requests.
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_MAX_AGE: int = 600


@functools.cache
def get_settings() -> APISettings:
    """Return the process-wide `APISettings`, reading the env once.

    In prod the OpenAPI schema is turned off, with no
    override: init kwargs take priority over env vars and `.env`. Common
    settings are built first, so an invalid common value (e.g.
    `DEPLOYMENT_ENV`) fails as a `CommonSettings` error.
    """
    overrides: dict[str, str | None] = {}
    if get_common_settings().DEPLOYMENT_ENV is DeploymentEnv.PROD:
        overrides = {"OPENAPI_URL": None}
    return APISettings(**overrides)
