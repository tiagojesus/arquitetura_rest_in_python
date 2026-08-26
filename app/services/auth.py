"""Service de autenticação (Spec 01) — concentra as regras de negócio JWT."""

import uuid
from datetime import UTC, datetime

import jwt
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.exceptions import AuthenticationError, ConflictError, InactiveUserError


async def register_user(session: AsyncSession, data: UserCreate) -> User:
    """Registra um novo usuário garantindo unicidade de email (RN01)."""
    repo = UserRepository(session)
    if await repo.get_by_email(data.email) is not None:
        raise ConflictError(f"Já existe um usuário com o email '{data.email}'.")
    user = User(
        email=data.email.lower(),
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
    )
    return await repo.create(user)


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User:
    """Autentica um usuário e atualiza last_login_at (RN04, RN08).

    Raises:
        AuthenticationError: se credenciais estiverem incorretas.
        InactiveUserError: se o usuário estiver desativado.
    """
    repo = UserRepository(session)
    user = await repo.get_by_email(email)
    if user is None or not verify_password(password, user.hashed_password):
        raise AuthenticationError()
    if not user.is_active:
        raise InactiveUserError()
    user.last_login_at = datetime.now(UTC)
    await repo.update(user)
    return user


async def get_current_user(session: AsyncSession, token: str) -> User:
    """Decodifica o JWT e retorna o usuário correspondente.

    Raises:
        AuthenticationError: se o token for inválido, expirado ou usuário não
            existir mais.
        InactiveUserError: se o usuário estiver desativado.
    """
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Token inválido ou expirado.") from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Token sem identificador de usuário.")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as exc:
        raise AuthenticationError("Identificador de usuário inválido.") from exc

    repo = UserRepository(session)
    user = await repo.get_by_id(user_uuid)
    if user is None:
        raise AuthenticationError("Usuário não encontrado.")
    if not user.is_active:
        raise InactiveUserError()

    return user


def generate_access_token(user: User) -> str:
    """Gera um JWT para o usuário informado."""
    return create_access_token(data={"sub": str(user.id)})
