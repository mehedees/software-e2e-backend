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

CORS is off until `CORS_ALLOW_ORIGINS` is set (comma-separated). The other `CORS_*` variables are listed in `core/settings.py`.

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
│   │       └── settings.py   env-driven settings (CORS)
│   └── worker/               background worker (empty)
└── libs/                     shared code (empty)
```

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
