"""Modelo da entidade Item (Spec 00)."""

import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    """Tabela `item` — CRUD de referência da arquitetura."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=120, unique=True, index=True)
    description: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
