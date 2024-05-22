from fastapi import APIRouter
from fastapi.responses import RedirectResponse

programmer_swaggerUi = APIRouter()

@programmer_swaggerUi.get("/docs", include_in_schema=False)
async def get_swagger_ui():
    return RedirectResponse("/redoc?lang=ru")

@programmer_swaggerUi.get("/redoc", include_in_schema=False)
async def get_redoc():
    return await get_swagger_ui()