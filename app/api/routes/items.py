"""Rotas do recurso Item (Spec 00).

Camada fina: apenas valida entrada (schema), chama o service e monta a
resposta. Erros de domínio são convertidos em HTTP pelos handlers globais
registrados em `app/main.py`.
"""

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services import item as item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate, session: AsyncSession = Depends(get_session)
) -> ItemRead:
    """Cria um novo item."""
    return await item_service.create_item(session, data)


@router.get("", response_model=list[ItemRead])
async def list_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> Sequence[ItemRead]:
    """Lista itens com paginação."""
    return await item_service.list_items(session, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> ItemRead:
    """Busca um item pelo id."""
    return await item_service.get_item(session, item_id)


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: uuid.UUID,
    data: ItemUpdate,
    session: AsyncSession = Depends(get_session),
) -> ItemRead:
    """Atualiza parcialmente um item."""
    return await item_service.update_item(session, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> None:
    """Remove um item."""
    await item_service.delete_item(session, item_id)
