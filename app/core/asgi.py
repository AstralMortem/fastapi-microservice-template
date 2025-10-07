from fastapi import FastAPI
from app.conf import settings
from app.api import global_router
from app.core.exceptions import register_exception
from contextlib import asynccontextmanager, AsyncExitStack, AbstractAsyncContextManager


def lifespan_manager(extra_lifespan: list[AbstractAsyncContextManager] = []):
    """Manage the lifespan of the FastAPI application with additional context managers."""
    @asynccontextmanager
    async def _lifespan(app: FastAPI):
        async with AsyncExitStack() as stack:
            for ctx in extra_lifespan:
                await stack.enter_async_context(ctx(app))
            yield

    return _lifespan


def create_app(extra_lifespan: list[AbstractAsyncContextManager] = []) -> FastAPI:
    lifespan = lifespan_manager(
        [
            # Add your lifespan context managers here
            *extra_lifespan
        ]
    )

    # Create FastAPI apps
    app = FastAPI(
        debug=settings.DEBUG, title=settings.SERVICE_NAME, version=settings.VERSION, lifespan=lifespan
    )

    # Register routers
    app.include_router(global_router)

    # Register exception handlers
    register_exception(app)

    return app
