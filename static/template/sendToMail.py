from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import BaseModel, EmailStr

# Модель для рассылки почты
class MailRequest(BaseModel):
    email: EmailStr  
    token: str 
    generatePassword: str
    login: str

# Конфиг для рассылки
conf = ConnectionConfig(
   MAIL_PORT=465,
   MAIL_SERVER="smtp.mail.ru",
   MAIL_USERNAME="dkorney@inbox.ru",
   MAIL_STARTTLS=False,
   MAIL_SSL_TLS=True,
   MAIL_FROM="dkorney@inbox.ru",
   MAIL_PASSWORD="mxqTC02Wj1p6v1PJKAUg",
)

# Создание письма
async def send_email(mail_request: dict, ip: str):
    message = MessageSchema(
       subject="Fastapi-Mail module",
       recipients=[mail_request.email],   
       body=f"""
        <div style="text-align: center;">
           <img src=`http://{ip}:8000/images/logo.webp` alt="Описание изображения" style="width: 190px; height: 190px;">
        </div>

        <p>Здравствуйте,</p>

        <p>Мы рады приветствовать вас в нашей компании! Ниже приведена ваша ссылка для проверки почты:</p>
         <p>Логин: {mail_request.login}</p>
         <p>Пароль: {mail_request.token}</p>

         <a href="http://{ip}:8000/Verification/eew">http://{ip}:8000/Verification/eew</a>

        <p>Пожалуйста, перейдите по этой ссылке для активации вашей учетной записи. Если у вас возникнут какие-либо вопросы или затруднения, не стесняйтесь обращаться в нашу службу поддержки.</p>

        <p>С уважением, ТОО "ВИТКОН Сервис"</p>
        """,
        subtype="html"
    )
   
    fm = FastMail(conf)
    await fm.send_message(message)