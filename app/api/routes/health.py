"""Rota de health check (Spec 00)."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Verifica que a API está no ar."""
    return {"status": "ok"}
