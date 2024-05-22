from datetime import datetime

# Получение сегодняшней даты
def get_current_date():
    current_date = datetime.now().date()
    return {"current_date": current_date}