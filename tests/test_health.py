"""Testes da rota de health check (Spec 00 — T06)."""

from httpx import AsyncClient


async def test_health_retorna_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
