"""Schemas relacionados à autenticação JWT (Spec 01)."""

from sqlmodel import SQLModel


class Token(SQLModel):
    """Resposta de login com JWT."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Payload interno decodificado de um JWT."""

    sub: str | None = None
