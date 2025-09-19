from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.settings import db
from sqlmodel import SQLModel

engine = create_async_engine(
    url=db.url,
    echo=db.echo,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_db() -> None:
    await engine.dispose()

# Dependency for FastAPI
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
