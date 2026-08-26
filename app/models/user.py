"""Modelo da entidade User (Spec 01)."""

import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Tabela `user` — autenticação JWT."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    full_name: str = Field(max_length=120)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    last_login_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
