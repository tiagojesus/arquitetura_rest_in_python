"""Repositório do agregado User (Spec 01)."""

import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user import User


class UserRepository:
    """Encapsula todas as queries da entidade User.

    Recebe a sessão no construtor e nunca retorna schemas — apenas models.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Busca um usuário pelo identificador."""
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        """Busca um usuário pelo email (case-insensitive)."""
        result = await self.session.exec(
            select(User).where(User.email == email.lower())
        )
        return result.first()

    async def create(self, user: User) -> User:
        """Persiste um novo usuário."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Persiste alterações de um usuário existente."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
