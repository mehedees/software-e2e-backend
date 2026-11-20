# software-e2e-backend

Another FastAPI boilerplate.

## Stack

- Python 3.15.2 (see `.python-version`)
- [FastAPI](https://fastapi.tiangolo.com/), Pydantic v2 / pydantic-settings
- SQLAlchemy 2.x
- Uvicorn
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Ruff](https://docs.astral.sh/ruff/) and [pre-commit](https://pre-commit.com/) for linting and formatting

## Getting started

```sh
uv sync                        # install dependencies
uv run pre-commit install      # enable git hooks
```

## Development

```sh
uv run ruff check .            # lint (add --fix to autofix)
uv run ruff format .           # format
uv run pre-commit run --all-files
```

Ruff is configured in `ruff.toml`.

## Commit messages

Commits must follow [Conventional Commits](https://www.conventionalcommits.org/), enforced by a `commit-msg` pre-commit hook:

```
type(optional-scope): short description
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

Examples: `feat(auth): add token refresh`, `fix: handle empty payload`.

`uv run pre-commit install` installs both the `pre-commit` and `commit-msg` hooks.

## Running

TBD...

## License

See [LICENSE](LICENSE).
