"""Utilitários puramente criptográficos e JWT.

Nenhuma regra de negócio ou dependência de framework deve residir aqui.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash armazenado."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto plano."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Codifica um JWT com os claims fornecidos.

    Args:
        data: Dicionário com claims a serem incluídos no payload.
        expires_delta: Tempo até a expiração; usa o default das settings se None.

    Returns:
        String do token JWT assinado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica e valida um token JWT.

    Args:
        token: String do token JWT.

    Returns:
        Payload decodificado como dicionário.

    Raises:
        jwt.PyJWTError: Se o token for inválido ou expirado.
    """
    return jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )
