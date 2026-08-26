"""Rotas de autenticação (Spec 01)."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user
from app.db import get_session
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth import (
    authenticate_user,
    generate_access_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    """Registra um novo usuário."""
    return await register_user(session, data)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    """Autentica um usuário e retorna um JWT Bearer."""
    user = await authenticate_user(session, form_data.username, form_data.password)
    access_token = generate_access_token(user)
    return Token(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Logout semântico: instrui o client a descartar o token (RN07)."""
    return {"detail": "Logout realizado com sucesso. Descarte o token no client."}


@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Retorna os dados do usuário autenticado."""
    return current_user
