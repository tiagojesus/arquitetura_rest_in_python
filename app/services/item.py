"""Service do recurso Item (Spec 00) — concentra as regras de negócio."""

import uuid
from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.item import Item
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.exceptions import ConflictError, NotFoundError


async def create_item(session: AsyncSession, data: ItemCreate) -> Item:
    """Cria um item garantindo a unicidade do nome (RN02)."""
    repo = ItemRepository(session)
    if await repo.get_by_name(data.name) is not None:
        raise ConflictError(f"Já existe um item com o nome '{data.name}'.")
    item = Item(name=data.name, description=data.description)
    return await repo.create(item)


async def list_items(session: AsyncSession, skip: int = 0, limit: int = 50) -> Sequence[Item]:
    """Lista itens com paginação (RN04)."""
    return await ItemRepository(session).list(skip=skip, limit=limit)


async def get_item(session: AsyncSession, item_id: uuid.UUID) -> Item:
    """Busca um item por id ou levanta NotFoundError."""
    item = await ItemRepository(session).get_by_id(item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} não encontrado.")
    return item


async def update_item(session: AsyncSession, item_id: uuid.UUID, data: ItemUpdate) -> Item:
    """Atualiza parcialmente um item, validando unicidade do nome (RN02)."""
    repo = ItemRepository(session)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} não encontrado.")

    if data.name is not None and data.name != item.name:
        if await repo.get_by_name(data.name) is not None:
            raise ConflictError(f"Já existe um item com o nome '{data.name}'.")
        item.name = data.name
    if data.description is not None:
        item.description = data.description

    return await repo.update(item)


async def delete_item(session: AsyncSession, item_id: uuid.UUID) -> None:
    """Remove um item (hard delete, RN03)."""
    repo = ItemRepository(session)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} não encontrado.")
    await repo.delete(item)
