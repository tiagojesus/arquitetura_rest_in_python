"""Seed de dados iniciais (Spec 02, ajustada pela Spec 03).

As credenciais do administrador vêm das Settings (variáveis de ambiente
ADMIN_EMAIL e ADMIN_INITIAL_PASSWORD) — nunca hard-coded (RN02 da spec 03).
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


async def seed_admin_user(session: AsyncSession) -> None:
    """Cria o usuário admin padrão se ele ainda não existir (RN01, idempotente)."""
    result = await session.exec(select(User).where(User.email == settings.admin_email))
    if result.first() is not None:
        return

    admin = User(
        email=settings.admin_email,
        full_name="Administrador",
        hashed_password=get_password_hash(settings.admin_initial_password),
        is_active=True,
    )
    session.add(admin)
    await session.commit()
