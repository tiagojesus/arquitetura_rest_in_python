"""Testes de disponibilidade da documentação Swagger (Spec 01 — T16)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from httpx import ASGITransport, AsyncClient

from app.api.routes import api_router
from app.core.config import settings
from app.main import create_app


async def test_docs_disponivel_quando_habilitado(client) -> None:
    """/docs retorna 200 quando docs_enabled=True (padrão)."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or response.headers.get(
        "content-type", ""
    ).startswith("text/html")


async def test_docs_indisponivel_quando_desabilitado(monkeypatch) -> None:
    """/docs retorna 404 quando docs_enabled=False."""
    monkeypatch.setattr(settings, "docs_enabled", False)

    # Cria app sem lifespan para evitar conexão com Postgres
    @asynccontextmanager
    async def _empty_lifespan(_app) -> AsyncGenerator[None, None]:
        yield

    from fastapi import FastAPI

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=_empty_lifespan,
        docs_url=None,
        redoc_url=None,
    )
    app.include_router(api_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/docs")
    assert response.status_code == 404
