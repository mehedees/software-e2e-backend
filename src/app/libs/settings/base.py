from importlib.metadata import metadata
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Distribution name in pyproject.toml.
_DISTRIBUTION = "software-e2e-backend"


def package_metadata(key: str) -> str:
    """Read a field (`Name`, `Summary`, `Version`, ...) of this project's package
    metadata, i.e. pyproject.toml as installed by `uv sync`."""
    return metadata(_DISTRIBUTION)[key]


def split_csv(value: object) -> object:
    """Split a comma-separated string into stripped, non-empty items.

    Values that aren't strings (e.g. a list passed in code) pass through.
    """
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


# A `list[str]` read from one comma-separated env var, e.g. `a.com, b.com`.
# `NoDecode` stops pydantic-settings from parsing the value as JSON first.
CommaSeparatedList = Annotated[list[str], NoDecode, BeforeValidator(split_csv)]


class BaseAppSettings(BaseSettings):
    """Base for every settings class: `CommonSettings` and each service's.

    It holds the configuration they all share and must never define fields,
    or a subclass's `env_prefix` would rename them (`MYSQL_HOST` would become
    `API_MYSQL_HOST`). Subclasses set only `env_prefix` in their own
    `model_config`; pydantic merges the rest from here.

    - `extra="ignore"`: one shared `.env` can hold every service's keys.
    - `case_sensitive=True`: env names must be upper case, matching the field
      names. A lowercase key is ignored.
    - `hide_input_in_errors=True`: a validation error names the field but
      doesn't echo the input, which would otherwise include secrets such as
      `MYSQL_PASSWORD` in startup logs.

    Naming rules are in ADR 0002 (`docs/adr/0002-settings-management.md`).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        hide_input_in_errors=True,
    )
