from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv

from backend.config import settings

load_dotenv()

DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL
)

AsyncSessLocal = async_sessionmaker(
    engine,
    class_ = AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessLocal() as session:
        yield session


        