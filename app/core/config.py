"""Configurações da aplicação lidas de variáveis de ambiente.

Nenhum valor sensível deve ser hard-coded fora dos defaults de
desenvolvimento local. Em produção, tudo vem do ambiente/.env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações globais da aplicação."""

    app_name: str = "Arquitetura REST"
    debug: bool = False
    database_url: str = "postgresql+psycopg://app:troque-esta-senha@localhost:5432/appdb"

    # Segurança JWT — em produção, secret_key deve vir exclusivamente do ambiente
    secret_key: str = "super-secret-dev-key-change-immediately"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Documentação Swagger /docs
    docs_enabled: bool = True
    secret_key: str = "super-secret-dev-key-change-immediately"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
