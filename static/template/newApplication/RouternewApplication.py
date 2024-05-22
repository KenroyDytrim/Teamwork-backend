# Нужные библиотеки
from fastapi import APIRouter, Depends, HTTPException
from ..criptoPassword import encrypt
from ..randomPassword import generate_temp_password
from ..sendToMail import MailRequest, send_email
import secrets
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.database_app import engine_a
from models_db.models_request import Address, Client, ClientAddress, Company, Requests, RequestStatusHistory
from .models import RequestModel
from datetime import datetime
from database.database_app import get_session

# Создание роутера
new_application = APIRouter()

# Функция для поиска клиента
async def search_clients(session, request):
    existing_client = await session.execute(select(Client).filter(Client.email == request.email, Client.phone == request.nomer))
    existing_client = existing_client.fetchone()
    if existing_client:
        return existing_client[0].id
    else:
        generate_password = generate_temp_password()
        new_password = encrypt(generate_password)
        token = secrets.token_hex(16)
        client = Client(
            lastname=request.lastname,
            firstname=request.firstname,
            middlename=request.middlename,
            phone=request.nomer,
            email=request.email,
            login=request.email,
            password=new_password["content"],
            iv=new_password["iv"],
            emailtoken=token
        )
        await send_email(MailRequest(email=request.email, token=generate_password, generatePassword=new_password["content"]))
        session.add(client)
        await session.commit()
        await session.refresh(client)
        return client.id

# Функция для добавления фирмы
async def create_company(session, companyName):
    new_company = Company(
        name=companyName,
        accounturl=''
    )
    session.add(new_company)
    await session.commit()
    await session.refresh(new_company)
    return new_company.id

# Функция для поиска адреса
async def search_adres(session, typeClient, street, houseNumber, apartmentOrOffice, company):
    if typeClient == 'Бизнес':
        address_query = (
            select(Address)
            .join(Company)  
            .filter(
                Address.street == street,
                Address.house == houseNumber,
                Address.office == apartmentOrOffice,
                Company.name == company 
            )
        )
    else:
        address_query = (
            select(Address)
            .filter(
                Address.street == street,
                Address.house == houseNumber,
                Address.office == apartmentOrOffice,
                Address.companyid == None  
            )
        )
    existing_adres = await session.execute(address_query)
    return existing_adres.fetchone()

# Функция для получения адреса
async def get_adres(session, request):
    existing_adres = await search_adres(session, request.typeClient, request.street, request.houseNumber, request.apartmentOrOffice, request.companyName)
    if existing_adres:
        return existing_adres[0].id
    else:
        if request.typeClient == "Бизнес":
            company = await create_company(session, request.companyName)
        else:
            company = None

        new_address = Address(
            street=request.street,
            house=request.houseNumber,
            office=request.apartmentOrOffice,
            companyid=company,
        )
        session.add(new_address)
        await session.commit()
        await session.refresh(new_address)
        return new_address.id

# Создание заявки
async def createRequest(session, request, clientid, adresid):

    new_request = Requests(
                requestnumber=1,
                statusid=1,
                paymentstatusid=1,
                employeeid=None,
                clientid=clientid,
                addressid=adresid,
                reason=request.problema,
                comment=request.comments,
                submissiondate=datetime.now().date(),
                completiondate=None,
                estimation=None,
                actid=None,
                revenue=len(request.comments)*100.25,
                expenses=None,
                profit=None
            )
    session.add(new_request)
    await session.commit()
    await session.refresh(new_request)
    return new_request.id

async def createStatusRequest(session, request_id):
    current_date = datetime.now().date()  
    current_time = datetime.now().time()  

    RequestStatus = RequestStatusHistory(
        requestid = request_id,
        statusid = 1,
        date = current_date,
        time = current_time
    )
    session.add(RequestStatus)
    await session.commit()
    await session.refresh(RequestStatus)

# Получение новой заявки
@new_application.put("/request")
async def create_request(request: RequestModel):
    print("Получение новой заявки")
    async with AsyncSession(engine_a) as session:
        client_id = await search_clients(session, request)
        address_id = await get_adres(session, request)
        existing_address_client = await session.execute(select(ClientAddress).filter(ClientAddress.clientid == client_id, ClientAddress.addressid == address_id))
        existing_address_client = existing_address_client.fetchone()
        if existing_address_client:
            new_request = await createRequest(session, request,client_id,address_id)
            await createStatusRequest(session, new_request)
            return {"message": f"Заявка принята {client_id} -------{address_id}"}
        else:
            client_address = ClientAddress(
                clientid=client_id,
                addressid=address_id
            )
            session.add(client_address)
            await session.commit()
            new_request = await createRequest(session, request,client_id,address_id)
            await createStatusRequest(session, new_request)
            return {"message": f"Заявка принята {client_id} -------{address_id}"}

# Подтверждение выполнения заявки и оценка качества работы
@new_application.post("/completeRequest")
async def complete_request(id:str, estimation:int, session: AsyncSession = Depends(get_session)):
    try:
            request = await session.get(Requests, id)
            
            if request is None:
                return JSONResponse(status_code=404, content={"message": "Заявка не найдена"})

            if request.statusid==1:
                request.statusid = 2
                request.completiondate = datetime.now().date()
                request.estimation = estimation

                time = (request.submissiondate-request.completiondate).days+1
                request.expenses = time * 250.50

                request.profit = float(request.revenue) - request.expenses

                request.paymentstatusid = 2
                
                await session.commit()
                return {"message": "Заявка выполнена"}
            else:
                return {"message": "Заявка уже выполнена"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')