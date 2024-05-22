# Нужные библиотеки
from fastapi import APIRouter, HTTPException, Path
from database.database_app import engine_a

from static.template.directorComponent.director.classes_analitycs.requests_statuses import requeestsStatusesService
from static.template.directorComponent.director.classes_analitycs.requests_payments import requeestsPaymentsService

# Создание роутера
director_analytic = APIRouter()

# Аналитика выполнения заявок за заданный период времени
@director_analytic.get('/getDataStatussesAnalytic/{start_date}/{end_date}')
async def send_data_table(start_date: str = Path(...), end_date: str = Path(...)):
    try:
        statusRequests = requeestsStatusesService(engine_a)

        status_names = await statusRequests.get_status_names()
        return await statusRequests.get_count_status_from_dates( status_names, start_date, end_date)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')
   
# Аналитика оплаты работы за заданный период времени
@director_analytic.get('/getDataPaymentsAnalytic/{start_date}/{end_date}')
async def send_data_table(start_date: str = Path(...), end_date: str = Path(...)):
    try:
        PaymentsRequests = requeestsPaymentsService(engine_a)

        payment_names = await PaymentsRequests.get_payment_names()
        return await PaymentsRequests.get_count_payment_from_dates( payment_names, start_date, end_date)
         
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')