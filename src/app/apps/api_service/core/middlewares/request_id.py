import re
from collections.abc import Iterable
from uuid import uuid7

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.apps.api_service.core.middlewares.context import get_request_context

REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"
CORRELATION_ID_HEADERS = ("X-Correlation-ID",)

# Inbound ids end up in logs and response headers, so only short values made of
# safe characters are accepted. Anything else is dropped as if it wasn't sent.
_VALID_ID = re.compile(r"[A-Za-z0-9._:\-]{1,128}")


def _clean_id(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if _VALID_ID.fullmatch(value) else None


def generate_trace_id() -> str:
    """Return a new unique trace id (UUIDv7, so ids sort by creation time)."""
    return uuid7().hex


class RequestIDMiddleware:
    """Store the request's ids in the `RequestContext`.

    - `request_id`: the id the client sent in `X-Request-ID`, if any.
    - `correlation_id`: the id a gateway, proxy or upstream service sent in one
      of `correlation_id_headers` (the first valid one wins), if any.
    - `trace_id`: always newly generated for this request, so it is unique even
      when a client reuses a request id.

    Inbound values that are too long or contain unexpected characters are
    ignored. The response echoes `X-Request-ID` (when the client sent one) and
    adds `X-Trace-ID`, so a client can quote the trace id when reporting a
    problem.

    Needs `RequestContextMiddleware` outside it: register it above that one in
    `core.bootstrap.middlewares`.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        request_id_header: str = REQUEST_ID_HEADER,
        correlation_id_headers: Iterable[str] = CORRELATION_ID_HEADERS,
    ) -> None:
        self.app = app
        self.request_id_header = request_id_header
        self.correlation_id_headers = tuple(correlation_id_headers)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        ctx = get_request_context()
        ctx.request_id = _clean_id(headers.get(self.request_id_header))
        ctx.correlation_id = next(
            (
                cleaned
                for name in self.correlation_id_headers
                if (cleaned := _clean_id(headers.get(name)))
            ),
            None,
        )
        ctx.trace_id = generate_trace_id()

        async def send_with_ids(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = MutableHeaders(scope=message)
                if ctx.request_id is not None:
                    response_headers[self.request_id_header] = ctx.request_id
                if ctx.trace_id is not None:
                    response_headers[TRACE_ID_HEADER] = ctx.trace_id
            await send(message)

        await self.app(scope, receive, send_with_ids)
