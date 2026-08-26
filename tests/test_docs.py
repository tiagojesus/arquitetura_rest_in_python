"""Testes de disponibilidade da documentação Swagger (Spec 01 — T16).

Ambos os cenários usam a factory real `create_app()` — o que está sob
teste é o comportamento verdadeiro da aplicação conforme a flag
`docs_enabled` (T08 da spec 03).
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import create_app


async def test_docs_disponivel_quando_habilitado(client: AsyncClient) -> None:
    """/docs retorna 200 quando docs_enabled=True (padrão)."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or response.headers.get(
        "content-type", ""
    ).startswith("text/html")


async def test_docs_indisponivel_quando_desabilitado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """/docs retorna 404 quando docs_enabled=False, usando create_app real."""
    monkeypatch.setattr(settings, "docs_enabled", False)
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/docs")
    assert response.status_code == 404
