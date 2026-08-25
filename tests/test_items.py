"""Testes do CRUD de Item (Spec 00 — T06)."""

import uuid

from httpx import AsyncClient


async def test_criar_item_caminho_feliz(client: AsyncClient) -> None:
    response = await client.post(
        "/items", json={"name": "Caderno", "description": "Caderno de 200 páginas"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Caderno"
    assert body["description"] == "Caderno de 200 páginas"
    assert uuid.UUID(body["id"])


async def test_criar_item_nome_duplicado_retorna_409(client: AsyncClient) -> None:
    await client.post("/items", json={"name": "Caderno"})
    response = await client.post("/items", json={"name": "Caderno"})
    assert response.status_code == 409
    assert "detail" in response.json()


async def test_listar_items(client: AsyncClient) -> None:
    await client.post("/items", json={"name": "Item A"})
    await client.post("/items", json={"name": "Item B"})
    response = await client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_buscar_item_inexistente_retorna_404(client: AsyncClient) -> None:
    response = await client.get(f"/items/{uuid.uuid4()}")
    assert response.status_code == 404
    assert "detail" in response.json()


async def test_atualizar_item_caminho_feliz(client: AsyncClient) -> None:
    created = (await client.post("/items", json={"name": "Caneta"})).json()
    response = await client.patch(
        f"/items/{created['id']}", json={"description": "Caneta azul"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Caneta azul"


async def test_atualizar_item_inexistente_retorna_404(client: AsyncClient) -> None:
    response = await client.patch(f"/items/{uuid.uuid4()}", json={"name": "X"})
    assert response.status_code == 404


async def test_deletar_item_caminho_feliz(client: AsyncClient) -> None:
    created = (await client.post("/items", json={"name": "Borracha"})).json()
    response = await client.delete(f"/items/{created['id']}")
    assert response.status_code == 204
    assert (await client.get(f"/items/{created['id']}")).status_code == 404


async def test_deletar_item_inexistente_retorna_404(client: AsyncClient) -> None:
    response = await client.delete(f"/items/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_criar_item_payload_invalido_retorna_422(client: AsyncClient) -> None:
    response = await client.post("/items", json={"description": "sem nome"})
    assert response.status_code == 422
