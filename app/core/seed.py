"""Seed de dados iniciais (Spec 02)."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User


async def seed_admin_user(session: AsyncSession) -> None:
    """Cria o usuário admin padrão se ele ainda não existir (RN01)."""
    result = await session.exec(select(User).where(User.email == "admin"))
    if result.first() is not None:
        return

    admin = User(
        email="admin",
        full_name="Administrador",
        hashed_password=get_password_hash("Admin0."),
        is_active=True,
    )
    session.add(admin)
    await session.commit()
