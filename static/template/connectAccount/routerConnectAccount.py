# Нужные библиотеки
from fastapi import APIRouter, HTTPException, Request
from static.template.token import generateToken
from fastapi.responses import JSONResponse
from database.database_app import  engine_a
from models_db.models_request import Client, Employee, Position
from sqlalchemy.ext.asyncio import AsyncSession
from ..criptoPassword import decrypt, encrypt
from ..randomPassword import generate_temp_password
from ..sendToMail import MailRequest, send_email
from sqlalchemy.future import select
from .setModels import ConnectModel, registrationModel

# Создание роутера
personal_account = APIRouter()

# Авторизация клиента
@personal_account.post("/user")
async def connection(request: ConnectModel):
   async with AsyncSession(engine_a) as session:

        login = request.UserLogin
        password = request.UserPassword

        if not login or not password:
            raise HTTPException(status_code=400, detail="Логин и пароль обязательны.")

        client = await session.execute(select(Client).filter(Client.login == login))
        client = client.scalar()
        if client:
            decrypted_password = decrypt({"iv": client.iv, "content": client.password})
            if decrypted_password == password:
                payload_client = {
                    "user_id": str(client.id),
                    "LastName": client.lastname,
                    "FirstName": client.firstname,
                    "MiddleName": client.middlename,
                    "Email": client.email,
                    "Phone": client.phone
                }
                token_client = generateToken(payload_client)
                return JSONResponse(content={"success": True, "redirect": f"/Client/{client.id}", "token": token_client})
            else:
                raise HTTPException(status_code=401, detail="Неверный логин или пароль.")

        employee = await session.execute(select(Employee).filter(Employee.login == login))
        employee = employee.scalar()
        if employee:
            decrypted_password = decrypt({"iv": employee.iv, "content": employee.password})
            print("decrypted_password = ",decrypted_password)
            if decrypted_password == password:
                position = await session.execute(select(Position).filter(Position.id == employee.positionid))
                position = position.scalar()
                if position:
                    title = position.name
                    if title == 'Программист':
                        payload_employee = {
                            "user_id": str(employee.id),
                            "LastName": str(employee.lastname),
                            "FirstName": str(employee.firstname),
                            "MiddleName": str(employee.middlename),
                            "Email": str(employee.email),
                            "Phone": str(employee.phone),
                            "post": str(title)
                        }
                        token_employee = generateToken(payload_employee)
                        return JSONResponse(content={"success": True, "redirect": f"/Director/{employee.id}", "token": token_employee})

        raise HTTPException(status_code=401, detail="Неверный логин или пароль.")
        
# Регистрация клиента
@personal_account.put("/registration")
async def create(request: registrationModel, host: Request):
     async with AsyncSession(engine_a) as session:

        login = request.Login
        email = request.Email
        phone = request.Phone

        generatePassword = generate_temp_password()
        newPassword = encrypt(generatePassword)
        
        New_user = Client(
                lastname="",
                firstname="",
                middlename="",
                phone= phone,
                email=email,
                login=login,
                password=newPassword["content"],
                iv=newPassword["iv"],
                emailtoken='eew'
            )
        session.add(New_user)
        client_host = host.client.host
        await send_email(MailRequest(email=email, token=generatePassword, generatePassword=newPassword["content"], login=login), client_host)
        await session.commit()
        return JSONResponse(content={"success": True, "redirect": f"/Directors/"})