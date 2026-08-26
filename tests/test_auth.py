"""Testes de autenticação JWT (Spec 01 — T11) e seed admin (Spec 02)."""

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

from app.core.security import create_access_token
from tests.conftest import test_engine, test_session_factory


def _make_token(user_id: str, expires_delta: timedelta | None = None) -> str:
    return create_access_token({"sub": user_id}, expires_delta=expires_delta)


async def test_seed_admin_login_com_sucesso(client: AsyncClient) -> None:
    """Verifica que o seed criou o usuário admin e ele consegue logar."""
    response = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "Admin0."},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_seed_admin_idempotente(client: AsyncClient) -> None:
    """O seed não duplica o admin se já existir."""
    # O fixture `client` já subiu a app e rodou o seed uma vez.
    # Fazemos login com o admin para garantir que existe.
    response = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "Admin0."},
    )
    assert response.status_code == 200

    # Verifica diretamente no banco que existe apenas 1 admin
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlmodel import select
    from app.models.user import User

    async with test_session_factory() as session:
        result = await session.exec(select(User).where(User.email == "admin"))
        users = result.all()
        assert len(users) == 1


async def test_registro_caminho_feliz(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={
            "email": "teste@exemplo.com",
            "full_name": "Usuário Teste",
            "password": "Senha123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "teste@exemplo.com"
    assert body["full_name"] == "Usuário Teste"
    assert "id" in body
    assert "hashed_password" not in body
    assert "password" not in body


async def test_registro_email_duplicado_retorna_409(client: AsyncClient) -> None:
    payload = {
        "email": "dup@exemplo.com",
        "full_name": "Dup",
        "password": "Senha123",
    }
    assert (await client.post("/auth/register", json=payload)).status_code == 201
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert "detail" in response.json()


async def test_login_caminho_feliz(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": "login@exemplo.com",
            "full_name": "Login",
            "password": "Senha123",
        },
    )
    response = await client.post(
        "/auth/login",
        data={"username": "login@exemplo.com", "password": "Senha123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_login_credenciais_invalidas_retorna_401(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        data={"username": "naoexiste@exemplo.com", "password": "Errada123"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


async def test_login_usuario_inativo_retorna_403(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": "inativo@exemplo.com",
            "full_name": "Inativo",
            "password": "Senha123",
        },
    )

    # Desativa o usuário diretamente no banco de teste
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from sqlmodel import select
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.models.user import User

    async with async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )() as session:
        result = await session.exec(
            select(User).where(User.email == "inativo@exemplo.com")
        )
        user = result.first()
        assert user is not None
        user.is_active = False
        await session.commit()

    response = await client.post(
        "/auth/login",
        data={"username": "inativo@exemplo.com", "password": "Senha123"},
    )
    assert response.status_code == 403
    assert "detail" in response.json()


async def test_me_com_token_valido(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": "me@exemplo.com",
            "full_name": "Me",
            "password": "Senha123",
        },
    )
    login = await client.post(
        "/auth/login",
        data={"username": "me@exemplo.com", "password": "Senha123"},
    )
    token = login.json()["access_token"]
    response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@exemplo.com"


async def test_me_sem_token_retorna_401(client: AsyncClient) -> None:
    response = await client.get("/auth/me")
    assert response.status_code == 401


async def test_me_com_token_expirado_retorna_401(client: AsyncClient) -> None:
    token = _make_token(
        "12345678-1234-1234-1234-123456789abc",
        expires_delta=timedelta(seconds=-1),
    )
    response = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


async def test_logout_com_token_valido_retorna_200(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": "logout@exemplo.com",
            "full_name": "Logout",
            "password": "Senha123",
        },
    )
    login = await client.post(
        "/auth/login",
        data={"username": "logout@exemplo.com", "password": "Senha123"},
    )
    token = login.json()["access_token"]
    response = await client.post(
        "/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "detail" in response.json()


async def test_last_login_at_atualizado_apos_login(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={
            "email": "last@exemplo.com",
            "full_name": "Last",
            "password": "Senha123",
        },
    )

    # Primeiro login para obter o timestamp inicial
    login1 = await client.post(
        "/auth/login",
        data={"username": "last@exemplo.com", "password": "Senha123"},
    )
    token1 = login1.json()["access_token"]
    me1 = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token1}"}
    )
    last_login_1_str = me1.json()["last_login_at"]
    last_login_1 = datetime.fromisoformat(
        last_login_1_str.replace("Z", "+00:00")
    ).replace(tzinfo=None)

    # Segundo login deve atualizar o timestamp
    before = datetime.now(UTC).replace(tzinfo=None)
    login2 = await client.post(
        "/auth/login",
        data={"username": "last@exemplo.com", "password": "Senha123"},
    )
    after = datetime.now(UTC).replace(tzinfo=None)

    token2 = login2.json()["access_token"]
    me2 = await client.get(
        "/auth/me", headers={"Authorization": f"Bearer {token2}"}
    )
    last_login_2_str = me2.json()["last_login_at"]
    last_login_2 = datetime.fromisoformat(
        last_login_2_str.replace("Z", "+00:00")
    ).replace(tzinfo=None)

    assert last_login_1 <= last_login_2
    assert before <= last_login_2 <= after
