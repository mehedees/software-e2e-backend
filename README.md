# software-e2e-backend

Another FastAPI boilerplate.

## Stack

- Python 3.15.2 (see `.python-version`)
- [FastAPI](https://fastapi.tiangolo.com/) (pinned `<0.166.0`, see [API conventions](#api-conventions)), Pydantic v2 / pydantic-settings
- SQLAlchemy 2.x
- Uvicorn
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Ruff](https://docs.astral.sh/ruff/) and [pre-commit](https://pre-commit.com/) for linting and formatting

## Getting started

```sh
uv sync                        # install dependencies (installs `app` in editable mode)
uv run pre-commit install      # enable the pre-commit and commit-msg hooks
cp .env.example .env           # local settings, see [Settings](#settings)
```

## Development

```sh
uv run ruff check .            # lint (add --fix to autofix)
uv run ruff format .           # format
uv run pre-commit run --all-files
```

Ruff is configured in `ruff.toml`. No test runner is set up yet.

## Running

Once `app` is defined in `server.py`:

```sh
uv run uvicorn app.apps.api_service.server:app --reload
```

The API fails at startup unless the required common settings are set: `DEPLOYMENT_ENV`, the MySQL host, user, password and database, and `REDIS_HOST`.

CORS is off until `API_CORS_ALLOW_ORIGINS` is set (comma-separated; renamed from `CORS_ALLOW_ORIGINS`, which is now ignored). The other `API_CORS_*` variables are listed in `core/settings.py`.

## Layout

src layout, built with `uv_build` (module name `app`). Import as `app.<...>`.

```
docs/adr/                     architecture decision records
src/app/
├── apps/
│   ├── api_service/          FastAPI service
│   │   ├── server.py         app entry point
│   │   └── core/
│   │       ├── bootstrap/    lifespan, exception handler and middleware registrars
│   │       ├── errors/       APIException
│   │       ├── middlewares/  request context and request/trace ids (ASGI middlewares)
│   │       ├── schema/       APIResponse / APIErrorResponse envelopes
│   │       ├── router.py     project APIRouter
│   │       └── settings.py   APISettings (API_*)
│   └── worker/               background worker
│       └── settings.py       WorkerSettings (WORKER_*)
└── libs/                     shared code
    └── settings/
        ├── base.py           BaseAppSettings: shared settings config and helpers
        └── common.py         CommonSettings: config shared by all services
```

## Settings

Settings come from environment variables, with `.env` as a fallback. `.env.example` lists every key. The reasons behind the rules are in [ADR 0002](docs/adr/0002-settings-management.md).

| Kind | Class | Env var |
|---|---|---|
| Shared by all services (MySQL, Redis, ...) | `CommonSettings` in `libs/settings/common.py` | `<RESPONSIBILITY>_<KEY>`, e.g. `MYSQL_HOST` |
| Used by one service | that service's `settings.py` | `<SERVICE>_<RESPONSIBILITY>_<KEY>`, e.g. `API_CORS_ALLOW_ORIGINS` |

- Every settings class subclasses `BaseAppSettings`, which has no fields. A subclass sets only `env_prefix`.
- A service class never subclasses `CommonSettings`. Code reads `get_common_settings()` for shared values and the service's `get_settings()` for its own. Don't instantiate the classes directly.
- Field names are upper case, and env names are case-sensitive. A field name is the env var minus the service prefix (`CORS_ALLOW_ORIGINS` on `APISettings`).
- Common names never start with a service prefix. A new service picks a prefix no other service uses.
- Names describing the app or service itself have no responsibility part: `DEPLOYMENT_ENV` (`dev`, `sit`, `uat` or `prod`), `DEBUG` and `LOG_LEVEL` in `CommonSettings`, and `API_TITLE`, `API_VERSION`, `API_DOCS_URL` and the like in `APISettings`. Project name, description and version default to `pyproject.toml`.
- In prod (`DEPLOYMENT_ENV=prod`), the API's OpenAPI schema and doc pages are always off, and `DEBUG=true` prints a warning at startup.

## API conventions

Details and examples live in the code. This section lists the rules and where to look. The reasons behind them are in [ADR 0001](docs/adr/0001-api-responses-routing-and-errors.md).

- **Response bodies:** return `APIResponse[T]` on success and raise `APIException` for errors. Every error goes out as `APIErrorResponse`. See `core/schema/response.py`.
- **Routes:** register them on `app.apps.api_service.core.router.APIRouter`, not `fastapi.APIRouter` or `@app.get(...)`. It also serves the trailing-slash form of each path and documents the 422 response. See `core/router.py`.
- **Error statuses in OpenAPI:** declare them per route, e.g. `responses={409: {"model": APIErrorResponse}}`. Don't declare 422 app-wide.
- **Schema models:** use `#` comments, not docstrings. Pydantic publishes a model's docstring in `/docs`.
- **FastAPI upgrades:** the router relies on FastAPI's private `get_flat_params`. Before you raise the pin, follow the checklist at that import in `core/router.py`.

## Commit messages

Commits must follow [Conventional Commits](https://www.conventionalcommits.org/). A `commit-msg` pre-commit hook enforces this:

```
type(optional-scope): short description
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Examples: `feat(auth): add token refresh`, `fix: handle empty payload`.

## License

See [LICENSE](LICENSE).
