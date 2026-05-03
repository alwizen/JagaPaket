from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from config import settings
import logging

logger = logging.getLogger(__name__)

# Optimize connection pool for production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Test connection before using from pool
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=20,        # Connection pool size
    max_overflow=10,     # Max overflow connections
    connect_args={
        "connect_timeout": 10,
        "autocommit": False,
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()
