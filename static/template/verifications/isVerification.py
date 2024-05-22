# Нужные библиотеки
from fastapi import APIRouter
from database.database_app import engine_a
from models_db.models_request import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Создание роутера
isVerification = APIRouter()

# Верификация клиента
@isVerification.get("/{token}")
async def check_token_email(token):
    async with AsyncSession(engine_a) as session:

        existing_client = await session.execute(select(Client).filter(Client.emailtoken == str(token)))
        existing_client = existing_client.scalar()
        if existing_client:
  
            existing_client.emailtoken = ""   
            await session.commit()  
            return "Проверка"
        else:
            return "Не нужна"