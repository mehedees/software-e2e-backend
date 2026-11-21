from contextvars import ContextVar
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send


@dataclass(slots=True)
class RequestContext:
    """Per-request data, readable from anywhere the request runs.

    The middleware fills in the request fields. `RequestIDMiddleware` sets
    `request_id`, `correlation_id` and `trace_id`. Code further in (other
    middlewares, dependencies, endpoints, services) may put anything else in
    `extras`, e.g. the authenticated user's id. The object is
    shared for the whole request, so a value set in one place is seen in all
    the others, including outer middlewares after the endpoint returns.
    """

    method: str
    path: str
    client_host: str | None
    request_id: str | None = None  # sent by the client (`X-Request-ID`)
    correlation_id: str | None = None  # sent by a gateway / upstream service
    trace_id: str | None = None  # generated per request
    extras: dict[str, Any] = field(default_factory=dict)
    _started: float = field(default_factory=perf_counter, repr=False)

    @property
    def elapsed_ms(self) -> float:
        """Milliseconds since the middleware received the request."""
        return (perf_counter() - self._started) * 1000


_request_context: ContextVar[RequestContext | None] = ContextVar(
    "request_context", default=None
)


def get_request_context() -> RequestContext:
    """Return the current request's context.

    Raises `RuntimeError` outside a request (startup, shutdown, the worker) or
    when `RequestContextMiddleware` isn't installed. Use
    `get_request_context_or_none` where running outside a request is expected.
    """
    ctx = _request_context.get()
    if ctx is None:
        raise RuntimeError(
            "No request context: not inside a request handled by "
            "RequestContextMiddleware."
        )
    return ctx


def get_request_context_or_none() -> RequestContext | None:
    """Return the current request's context, or `None` outside a request."""
    return _request_context.get()


class RequestContextMiddleware:
    """Create a `RequestContext` for each HTTP / WebSocket request.

    Written as pure ASGI rather than `BaseHTTPMiddleware`, which runs the app in
    a separate task, so the context var is set in the same task as the
    endpoint and stays set through background tasks, which run before the
    response call returns.

    Add it last with `app.add_middleware(RequestContextMiddleware)` so it is
    the outermost user middleware and every other middleware can read it.

    It runs inside Starlette's `ServerErrorMiddleware`, so the context is
    already reset when the app-level `Exception` handler runs. Handlers for
    `APIException`, `HTTPException` and validation errors run inside it and
    can read the context.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        ctx = RequestContext(
            method=scope.get("method", "WEBSOCKET"),
            path=scope["path"],
            client_host=client[0] if client else None,
        )
        token = _request_context.set(ctx)
        try:
            await self.app(scope, receive, send)
        finally:
            _request_context.reset(token)
