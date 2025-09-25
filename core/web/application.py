import json
import logging
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI, HTTPException
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from starlette.middleware.cors import CORSMiddleware

from core.helpers.exception_handler import (
    CustomError,
    custom_http_exception_handler,
    http_exception_handler,
)
from core.log_handler import logger
from core.settings import settings
from core.web.api.router import api_router
from core.web.lifespan import lifespan_setup


APP_ROOT = Path(__file__).parent.parent


def setup_sentry() -> None:
    """Initialize Sentry if DSN is configured."""
    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=settings.sentry_sample_rate,
        environment=settings.environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            LoggingIntegration(
                level=logging.getLevelName(settings.log_level.value),
                event_level=logging.ERROR,
            ),
        ],
    )


def get_app() -> FastAPI:
    """Construct FastAPI application."""
    setup_sentry()

    app = FastAPI(
        title="Pixerse Chatbot",
        version="v0.0.1",
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Routers
    app.include_router(router=api_router, prefix="/api")

    # Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # app.add_middleware(AuthMiddleware)

    # Exception handlers
    app.add_exception_handler(CustomError, http_exception_handler)  # type: ignore
    app.add_exception_handler(HTTPException, custom_http_exception_handler)

    # Static files
    # app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app


# FastAPI app instance
app = get_app()