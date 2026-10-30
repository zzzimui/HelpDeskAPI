import os
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from app.database.migrations import Base
from app.modules.categories.models import Category
from app.modules.roles.models import Permissions, Role
from app.modules.users.models import User


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Obtém e valida a URL exclusiva do banco de testes."""
    url = os.getenv("TEST_DATABASE_URL")

    if not url:
        pytest.fail(
            "Defina TEST_DATABASE_URL para executar os testes "
            "de integração."
        )

    parsed_url = make_url(url)

    if parsed_url.database != "helpdesk_test":
        pytest.fail(
            "Os testes de integração só podem usar "
            "o banco helpdesk_test."
        )

    if parsed_url.drivername != "postgresql+asyncpg":
        pytest.fail(
            "TEST_DATABASE_URL deve usar postgresql+asyncpg."
        )

    return url


@pytest_asyncio.fixture
async def db_session(
    test_database_url: str,
) -> AsyncGenerator[AsyncSession, None]:
    """Fornece uma sessão isolada por teste, com rollback."""
    engine = create_async_engine(
        test_database_url,
        echo=False,
    )

    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()

            session = AsyncSession(
                bind=connection,
                expire_on_commit=False,
                autoflush=False,
                join_transaction_mode="create_savepoint",
            )

            try:
                yield session
            finally:
                await session.close()

                if transaction.is_active:
                    await transaction.rollback()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def customer_role(
    db_session: AsyncSession,
) -> Role:
    """Obtém o papel CUSTOMER criado pela migração."""
    result = await db_session.execute(
        select(Role).where(
            Role.permission == Permissions.CUSTOMER
        )
    )
    role = result.scalar_one_or_none()

    if role is None:
        pytest.fail(
            "O papel CUSTOMER não existe. "
            "Verifique a migração de papéis iniciais."
        )

    return role


@pytest_asyncio.fixture
async def customer_user(
    db_session: AsyncSession,
    customer_role: Role,
) -> User:
    """Cria um usuário de teste associado a CUSTOMER."""
    user = User(
        id=uuid4(),
        email=f"customer-{uuid4().hex}@example.com",
        hashed_password="not-a-real-password-hash",
        role_id=customer_role.id,
        is_active=True,
        is_superuser=False,
    )

    db_session.add(user)
    await db_session.flush()

    return user


@pytest_asyncio.fixture
async def hardware_category(
    db_session: AsyncSession,
) -> Category:
    """Obtém a categoria Hardware criada pela migração."""
    result = await db_session.execute(
        select(Category).where(
            Category.name == "Hardware"
        )
    )
    category = result.scalar_one_or_none()

    if category is None:
        pytest.fail(
            "A categoria Hardware não existe. "
            "Verifique as migrações iniciais."
        )

    return category
