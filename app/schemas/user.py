"""Schemas (DTOs) do recurso User (Spec 01)."""

import re
import uuid
from datetime import datetime

from pydantic import field_validator
from sqlmodel import SQLModel


class UserCreate(SQLModel):
    """Payload de criação de um usuário."""

    email: str
    full_name: str
    password: str

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def _validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("A senha deve ter no mínimo 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("A senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("A senha deve conter pelo menos um dígito")
        return v


class UserRead(SQLModel):
    """Representação pública de um usuário retornada pela API."""

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
