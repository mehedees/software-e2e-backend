from collections.abc import Callable

from fastapi import FastAPI


def create_fastapi_app(
    lifespan: Callable,
    exception_handler_registrar: Callable,
    middleware_registrar: Callable,
) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
    )
    exception_handler_registrar(app)
    middleware_registrar(app)
    return app
