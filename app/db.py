"""Infraestrutura de banco de dados: engine, sessão e inicialização."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependência FastAPI que fornece uma sessão de banco por request."""
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    """Cria as tabelas no banco.

    Adequado para o estágio atual do projeto. Quando o esquema começar a
    evoluir em produção, adotar Alembic (via spec própria).
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
