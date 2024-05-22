# Нужные библиотеки
from pydantic import BaseModel,EmailStr

# Модель для авторизации
class ConnectModel(BaseModel):
    UserLogin: str
    UserPassword: str

# Модель для регистрации
class registrationModel(BaseModel):
    Login: str
    Email: str
    Phone: str

# Модель для подтверждения почты
class MailRequest(BaseModel):
    email: EmailStr  
    token: str 
    generatePassword: str