# Нужная библиотека
from pydantic import BaseModel

# Модель заявки
class RequestModel(BaseModel):
    lastname: str
    firstname: str
    middlename: str
    email: str
    nomer: str
    problema: str
    comments: str
    street: str
    houseNumber: str
    apartmentOrOffice: str
    typeClient: str
    companyName: str