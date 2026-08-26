"""Exceções de domínio levantadas pelos services.

As rotas (ou handlers globais no main.py) convertem estas exceções em
respostas HTTP com o status semanticamente correto. Todas herdam de
DomainError, permitindo captura genérica quando necessário (RN03 da
spec 03).
"""


class DomainError(Exception):
    """Erro genérico de regra de negócio (mapeado para HTTP 400)."""

    def __init__(self, message: str = "Erro de domínio") -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(DomainError):
    """Recurso não encontrado (mapeado para HTTP 404)."""

    def __init__(self, message: str = "Recurso não encontrado") -> None:
        super().__init__(message)


class ConflictError(DomainError):
    """Conflito de estado/unicidade (mapeado para HTTP 409)."""

    def __init__(self, message: str = "Conflito de dados") -> None:
        super().__init__(message)


class AuthenticationError(DomainError):
    """Credenciais inválidas ou token não autorizado (HTTP 401)."""

    def __init__(self, message: str = "Credenciais inválidas") -> None:
        super().__init__(message)


class InactiveUserError(DomainError):
    """Usuário existe mas está desativado (mapeado para HTTP 403)."""

    def __init__(self, message: str = "Usuário inativo") -> None:
        super().__init__(message)
