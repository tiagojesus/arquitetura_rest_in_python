"""Exceções de domínio levantadas pelos services.

As rotas (ou handlers globais no main.py) convertem estas exceções em
respostas HTTP com o status semanticamente correto.
"""


class DomainError(Exception):
    """Erro genérico de regra de negócio."""


class NotFoundError(DomainError):
    """Recurso não encontrado (mapeado para HTTP 404)."""


class ConflictError(DomainError):
    """Conflito de estado/unicidade (mapeado para HTTP 409)."""
