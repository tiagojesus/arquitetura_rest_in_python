"""Schemas (DTOs) do recurso Item (Spec 00)."""

import uuid
from datetime import datetime

from sqlmodel import SQLModel


class ItemCreate(SQLModel):
    """Payload de criação de um item."""

    name: str
    description: str | None = None


class ItemUpdate(SQLModel):
    """Payload de atualização parcial — todos os campos opcionais."""

    name: str | None = None
    description: str | None = None


class ItemRead(SQLModel):
    """Representação pública de um item retornada pela API."""

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
