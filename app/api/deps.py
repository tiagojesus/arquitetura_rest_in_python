"""Dependencies compartilhadas da camada API."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.models.user import User
from app.services.auth import get_current_user as _get_current_user
from app.services.exceptions import AuthenticationError, InactiveUserError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Dependency que extrai e valida o JWT do header Authorization.

    Retorna o model User autenticado ou levanta HTTPException 401/403.
    """
    try:
        user = await _get_current_user(session, token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    return user
