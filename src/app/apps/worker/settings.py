import functools

from pydantic_settings import SettingsConfigDict

from app.libs.settings import BaseAppSettings


class WorkerSettings(BaseAppSettings):
    """Settings only the worker uses, read from `WORKER_*` environment variables.

    Fields are named `<RESPONSIBILITY>_<KEY>` and read from
    `WORKER_<RESPONSIBILITY>_<KEY>`. Shared settings (MySQL, Redis, ...) live
    in `app.libs.settings.CommonSettings`, not here.

    Read through `get_settings()`, not by instantiating this class.
    """

    model_config = SettingsConfigDict(env_prefix="WORKER_")


@functools.cache
def get_settings() -> WorkerSettings:
    """Return the process-wide `WorkerSettings`, reading the env once."""
    return WorkerSettings()
