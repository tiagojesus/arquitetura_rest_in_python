"""Repositório do agregado Item (Spec 00)."""

import uuid
from collections.abc import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.item import Item


class ItemRepository:
    """Encapsula todas as queries da entidade Item.

    Recebe a sessão no construtor e nunca retorna schemas — apenas models.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: uuid.UUID) -> Item | None:
        """Busca um item pelo identificador."""
        return await self.session.get(Item, item_id)

    async def get_by_name(self, name: str) -> Item | None:
        """Busca um item pelo nome (único)."""
        result = await self.session.exec(select(Item).where(Item.name == name))
        return result.first()

    async def list(self, skip: int = 0, limit: int = 50) -> Sequence[Item]:
        """Lista itens com paginação."""
        result = await self.session.exec(select(Item).offset(skip).limit(limit))
        return result.all()

    async def create(self, item: Item) -> Item:
        """Persiste um novo item."""
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update(self, item: Item) -> Item:
        """Persiste alterações de um item existente."""
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete(self, item: Item) -> None:
        """Remove um item (hard delete)."""
        await self.session.delete(item)
        await self.session.commit()
