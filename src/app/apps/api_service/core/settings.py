from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class CORSSettings(BaseSettings):
    """CORS settings, read from `CORS_*` environment variables.

    List values are comma-separated, e.g.
    `CORS_ALLOW_ORIGINS=https://app.example.com,http://localhost:3000`.
    With no origins set, CORS is off and browsers block cross-origin calls.
    """

    model_config = SettingsConfigDict(env_prefix="CORS_")

    allow_origins: Annotated[list[str], NoDecode] = []
    allow_methods: Annotated[list[str], NoDecode] = ["*"]
    allow_headers: Annotated[list[str], NoDecode] = ["*"]
    # Don't combine with `CORS_ALLOW_ORIGINS=*`: Starlette then echoes any
    # origin back, which lets every site make credentialed requests.
    allow_credentials: bool = False
    max_age: int = 600

    @field_validator("allow_origins", "allow_methods", "allow_headers", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
