import functools
import sys
from typing import Self

from pydantic import Field, SecretStr, model_validator

from app.libs.settings.base import BaseAppSettings, package_metadata
from app.libs.settings.enums import DeploymentEnv, LogLevel


class CommonSettings(BaseAppSettings):
    """Settings shared by every service: app info, MySQL, Redis and other backing services.

    Fields are named `<RESPONSIBILITY>_<KEY>` (e.g. `MYSQL_HOST`) and read from
    the env var of the same name. There is no prefix, so a name here must never
    start with a service prefix (`API_`, `WORKER_`, ...). A few app-wide flags
    (`DEBUG`, `LOG_LEVEL`) keep their conventional unprefixed names. Settings
    only one service uses belong in that service's settings class instead.

    Read through `get_common_settings()`, not by instantiating this class.
    """

    # Project info. Defaults come from pyproject.toml via the installed package.
    PROJECT_NAME: str = Field(default_factory=lambda: package_metadata("Name"))
    PROJECT_DESCRIPTION: str = Field(
        default_factory=lambda: package_metadata("Summary")
    )
    PROJECT_VERSION: str = Field(default_factory=lambda: package_metadata("Version"))

    DEPLOYMENT_ENV: DeploymentEnv
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = LogLevel.INFO

    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: SecretStr
    MYSQL_DATABASE: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    @model_validator(mode="after")
    def _warn_debug_in_prod(self) -> Self:
        if self.DEBUG and self.DEPLOYMENT_ENV is DeploymentEnv.PROD:
            # TODO: replace with a logger warning once logging is set up.
            print(
                "WARNING: DEBUG is enabled with DEPLOYMENT_ENV=prod",
                file=sys.stderr,
            )
        return self


@functools.cache
def get_common_settings() -> CommonSettings:
    """Return the process-wide `CommonSettings`, reading the env once."""
    return CommonSettings()
