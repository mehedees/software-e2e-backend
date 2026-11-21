from collections.abc import Callable
from typing import Any

from fastapi import APIRouter as FastAPIRouter

# `get_flat_params` is not public FastAPI API: it isn't documented, and
# `fastapi.dependencies.utils` has no `__all__`. FastAPI's own 422 rule
# (`fastapi/openapi/utils.py`, `get_openapi_path`) uses the private
# `_get_openapi_dependency_data` instead. As of 0.165 the two collect the same
# params (same dependency walk, same cache-key dedupe, same flattening of
# model params); FastAPI calls `get_flat_params` only to gather request models
# for `components`. pyproject pins `fastapi<0.166.0`, so these can only break
# on an upgrade.
#
# Loud failures (the app won't start):
# - Renamed, moved or removed: `ImportError` when this module is imported.
# - Signature changed (e.g. takes the route, or gains a required arg):
#   `TypeError` on the first route registration, i.e. at import of any
#   routes module.
#
# Silent failures (the app runs, OpenAPI is wrong):
# - Return type changed: if it returns a container or object that is always
#   truthy, every route gets a 422; if it always returns empty, only body
#   routes do.
# - Semantics drift: if FastAPI changes which params it counts for its own
#   422 (e.g. skipping `include_in_schema=False` params, or counting security
#   dependencies) without changing `get_flat_params`, the two disagree. A route
#   then either documents our 422 where FastAPI would add none, or skips ours
#   and FastAPI adds its default `HTTPValidationError` (the wrong schema, since
#   the handler always returns `APIErrorResponse`).
# - Param kinds: it returns path/query/header/cookie only; body is checked
#   separately through `probe.body_field`. If FastAPI adds a new param kind
#   that `get_flat_params` doesn't return, or moves body into it, the check
#   misses that input or counts it twice. Counting twice is harmless.
#
# On a FastAPI upgrade, check: build the same routes on stock
# `fastapi.APIRouter` and confirm the set of operations with a 422 in the
# generated OpenAPI matches the set ours documents. Re-read `get_openapi_path`
# for changes to the 422 condition.
from fastapi.dependencies.utils import get_flat_params
from fastapi.routing import APIRoute

from app.apps.api_service.core.schema.response import APIErrorResponse

_VALIDATION_ERROR_RESPONSE = {
    "model": APIErrorResponse,
    "description": "Validation Error",
}


class APIRouter(FastAPIRouter):
    """
    Use this class over fastapi.APIRouter
    """

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        include_in_schema: bool = True,
        **kwargs: Any,
    ) -> None:
        """Register the route at `path` and at its trailing-slash twin.

        `/users` and `/users/` both resolve without a redirect; the twin is
        hidden from OpenAPI. The route also gets a documented 422
        `APIErrorResponse` if it takes input (see `_with_validation_error`).
        """
        kwargs["responses"] = self._with_validation_error(path, endpoint, kwargs)
        alt_path = path[:-1] if path.endswith("/") else path + "/"
        super().add_api_route(alt_path, endpoint, include_in_schema=False, **kwargs)
        return super().add_api_route(
            path, endpoint, include_in_schema=include_in_schema, **kwargs
        )

    def _with_validation_error(
        self, path: str, endpoint: Callable[..., Any], kwargs: dict[str, Any]
    ) -> dict[int | str, dict[str, Any]]:
        """Return the route's `responses`, plus 422 if the route can fail validation.

        Matches FastAPI's own rule for its default 422 (`HTTPValidationError`)
        as of 0.165: only routes with path/query/header/cookie params or a
        body, counting params from this router's and the route's dependencies.
        It relies on `get_flat_params`; see the note at its import. A 422 / `4XX` /
        `default` declared on the route or this router is left as is.

        Dependencies added later via `include_router(..., dependencies=...)` or
        `FastAPI(dependencies=...)` aren't visible here; if only those take
        input, FastAPI's default `HTTPValidationError` schema shows instead,
        which is wrong because the handler always returns `APIErrorResponse`.

        Don't declare 422 app-wide in `FastAPI(responses=...)` either: FastAPI
        merges app-level responses into every route at `include_router` time,
        so this can't take it back off routes that take no input.
        """
        responses = dict(kwargs.get("responses") or {})
        declared = {*self.responses, *responses}
        if declared & {422, "422", "4XX", "default"}:
            return responses

        probe = APIRoute(
            self.prefix + path,
            endpoint,
            dependencies=[*self.dependencies, *(kwargs.get("dependencies") or [])],
        )
        if get_flat_params(probe.dependant) or probe.body_field:
            responses[422] = _VALIDATION_ERROR_RESPONSE
        return responses
