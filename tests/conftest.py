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

from app.modules.categories.models import Category
from app.modules.roles.models import Permissions, Role
from app.modules.users.models import User


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Obtain and validate the unique testbed URL"""
    url = os.getenv("TEST_DATABASE_URL")

    if not url:
        pytest.fail(
            "Define TEST_DATABASE_URL to run integration tests"
        )

    parsed_url = make_url(url)

    if parsed_url.database != "helpdesk_test":
        pytest.fail(
            "Integration tests can only use the helpdesk_test database."
        )

    if parsed_url.drivername != "postgresql+asyncpg":
        pytest.fail(
            "TEST_DATABASE_URL must use postgresql+asyncpg."
        )

    return url


@pytest_asyncio.fixture
async def db_session(
    test_database_url: str,
) -> AsyncGenerator[AsyncSession, None]:
    """Provides one isolated session per test, with rollback"""
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
    """Gets the CLIENT role created by the migration"""
    result = await db_session.execute(
        select(Role).where(
            Role.permission == Permissions.CUSTOMER
        )
    )
    role = result.scalar_one_or_none()

    if role is None:
        pytest.fail(
            "The CUSTOMER role does not exist. "
            "Check home role migration."
        )

    return role


@pytest_asyncio.fixture
async def customer_user(
    db_session: AsyncSession,
    customer_role: Role,
) -> User:
    """Create a test user associated with the client"""
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
    """Gets the Hardware category created by the migration"""
    result = await db_session.execute(
        select(Category).where(
            Category.name == "Hardware"
        )
    )
    category = result.scalar_one_or_none()

    if category is None:
        pytest.fail(
            "The Hardware category does not exist."
            "Check initial migrations."
        )

    return category
