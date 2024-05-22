# Нужные библиотеки
from sqlalchemy.ext.asyncio import create_async_engine
from .db_settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
# адрес базы данных для и асинхронного подключения
ur_a = settings.POSTGRES_DATABASE_URLA
# создание движков
engine_a = create_async_engine(ur_a, echo=True)
# подключение к базе данных
async def get_session():
    async with AsyncSession(engine_a) as session:
        try:
            yield session
        finally:
            await session.close()
