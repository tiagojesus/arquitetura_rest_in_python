"""Factory da aplicação FastAPI e ponto de entrada ASGI."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.config import settings
from app.db import init_db
from app.services.exceptions import ConflictError, DomainError, NotFoundError


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Inicializa recursos no startup (cria tabelas) e finaliza no shutdown."""
    await init_db()
    yield


def create_app() -> FastAPI:
    """Constrói e configura a instância da aplicação."""
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(_request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
        )

    app.include_router(api_router)
    return app


app = create_app()
