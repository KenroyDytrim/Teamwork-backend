# Нужные библиотеки
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from static.template.newApplication.RouternewApplication import new_application
from static.template.verifications.isVerification import isVerification
from static.template.connectAccount.routerConnectAccount import personal_account

from static.template.directorComponent.directorRouter import directorRouter
from static.template.client.clientRouter import clientRouter

from datetime import datetime
from contextlib import asynccontextmanager

# Занесение информации о включении и выключении в log.txt
@asynccontextmanager
async def lifespan(app: FastAPI):
    open("log.txt", mode="a").write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Begin\n')
    yield
    open("log.txt", mode="a").write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: End\n')

# Экземпляр FastAPI
app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Включаем роутеры
app.include_router(new_application, prefix="/ClientApplication", tags=["Request"])
app.include_router(isVerification, prefix="/Verification" , tags=["Verification client"])
app.include_router(personal_account, prefix="/personal_account")
app.include_router(directorRouter, prefix="/director")
app.include_router(clientRouter, prefix="/client", tags=["client"])

# Получение логотипа
@app.get("/images/logo.webp")
async def get_image():
    image_path = "static/images/logo.webp"
    return FileResponse(image_path)

# Начальная страница
@app.get("/")
async def read_root():
    return FileResponse("files/index.html")