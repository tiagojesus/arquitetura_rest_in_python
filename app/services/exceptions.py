"""Exceções de domínio dos services.

Estas exceções são levantadas pela camada de negócio e convertidas em
HTTPException pelas rotas.
"""


class DomainError(Exception):
    """Erro genérico de domínio / regra de negócio."""

    def __init__(self, message: str = "Erro de domínio") -> None:
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    """Credenciais inválidas ou token não autorizado."""

    def __init__(self, message: str = "Credenciais inválidas") -> None:
        self.message = message
        super().__init__(self.message)


class InactiveUserError(Exception):
    """Usuário existe mas está desativado."""

    def __init__(self, message: str = "Usuário inativo") -> None:
        self.message = message
        super().__init__(self.message)


class ConflictError(Exception):
    """Conflito de dados (ex.: email ou nome já existente)."""

    def __init__(self, message: str = "Conflito de dados") -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Recurso não encontrado."""

    def __init__(self, message: str = "Recurso não encontrado") -> None:
        self.message = message
        super().__init__(self.message)
    """Credenciais inválidas ou token não autorizado."""

    def __init__(self, message: str = "Credenciais inválidas") -> None:
        self.message = message
        super().__init__(self.message)


class InactiveUserError(Exception):
    """Usuário existe mas está desativado."""

    def __init__(self, message: str = "Usuário inativo") -> None:
        self.message = message
        super().__init__(self.message)
