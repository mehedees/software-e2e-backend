# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Early-stage FastAPI backend boilerplate: no application code, tests, or pre-commit config exist yet (only `pyproject.toml`, `ruff.toml`, `uv.lock`). Update this file as structure emerges.

## Stack

Python 3.15.2 (pinned in `.python-version`), managed with `uv`. FastAPI, Pydantic v2 / pydantic-settings, SQLAlchemy 2.x, Uvicorn. Dev tools: ruff, pre-commit (with pre-commit-uv).

## Commands

- Install deps: `uv sync`
- Lint: `uv run ruff check .` (add `--fix` to autofix)
- Format: `uv run ruff format .`
- Run server (once an app exists, e.g. `app/main.py`): `uv run uvicorn app.main:app --reload`

No test runner is configured yet; add one (e.g. pytest) to dev dependencies before writing tests.

## Conventions

- Commit messages must follow Conventional Commits (`type(scope): description`; types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert). Enforced by the `conventional-pre-commit` `commit-msg` hook in `.pre-commit-config.yaml`.
- Ruff config is in `ruff.toml` (target `py315`, line length 88, `app` as first-party for isort). `E501` and `B008` are ignored (the latter for FastAPI `Depends()` defaults).
