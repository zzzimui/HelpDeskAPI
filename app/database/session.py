from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

from collections.abc import AsyncGenerator

# Engine assíncrona configurada para PostgreSQL via asyncpg ou sqlite
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,           # Altere para True se quiser ver as queries SQL no console
    # pool_size=10,         # Tamanho do pool de conexões (ajustável)
    # max_overflow=20       # Conexões extras permitidas em picos de tráfego
)

AsyncSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session