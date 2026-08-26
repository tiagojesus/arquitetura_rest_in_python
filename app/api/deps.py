"""Dependencies compartilhadas da camada API."""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.user import User
from app.services.auth import get_current_user as _get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Dependency que extrai e valida o JWT do header Authorization.

    Retorna o model User autenticado. As exceções de domínio
    (AuthenticationError/InactiveUserError) propagam para os handlers
    globais registrados em `app/main.py`, único ponto de conversão
    domínio → HTTP (RN04 da spec 03).
    """
    return await _get_current_user(session, token)
