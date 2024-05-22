# Нужные библиотеки
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.database_app import engine_a
from models_db.models_request import Notes  

# Создание роутера
NotesRouter = APIRouter()

# Модель для заметок
class Note(BaseModel):
    title: str
    content: str
    employee_id: UUID4

# Создание заметки директора
@NotesRouter.post("/createNote")
async def create_note(newnote: Note):
    try:
        async with AsyncSession(engine_a) as session:
            new_note = Notes(
                title = newnote.title,
                content = newnote.content,
                employeeid = newnote.employee_id
            )
            session.add(new_note)
            await session.commit()
            
            return {"message": "Заметка успешно создана"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')

# Удаление заметки
@NotesRouter.delete("/deleteNote/{note_id}")
async def delete_note(note_id: str):
    try:
        async with AsyncSession(engine_a) as session:
            await session.execute(delete(Notes).where(Notes.id == note_id))
            await session.commit()
            
            check_query = (
                select(Notes)
                .where(Notes.id == note_id)
            )
            result = await session.execute(check_query)
            remaining_note = result.scalar_one_or_none()
            
            if remaining_note is not None:
                print(f"Заметка с ID {note_id} не удалена")
                raise HTTPException(status_code=404, detail=f'Заметка с ID {note_id} не найдена')
            else:
                print(f"Заметка с ID {note_id} успешно удалена")
                return {"message": "Заметка успешно удалена"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')

# Получение заметок о сотруднике
@NotesRouter.get("/getNotes/{employee_id}")
async def get_notes(employee_id: str):
    try:
        async with AsyncSession(engine_a) as session:
            query = (
                select(
                    Notes.id,
                    Notes.title,
                    Notes.content,
                    Notes.employeeid
                ) 
                .select_from(Notes)
                .where(Notes.employeeid == employee_id)
            )
            result = await session.execute(query)
            rows = result.fetchall()
            await session.commit()  
            
            return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')

# Изменение заметки
@NotesRouter.put("/updateNote/{note_id}")
async def update_note(note_id: str, note_data: Note):
    try:
        async with AsyncSession(engine_a) as session:

            note = await session.get(Notes, note_id)
            
            if note is None:
                raise HTTPException(status_code=404, detail="Заметка не найдена")
            
            for field, value in note_data.dict(exclude_unset=True).items():
                setattr(note, field, value)
            
            await session.commit()
            
            return {"message": f"Заметка с ID {note_id} успешно обновлена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Ошибка сервера: {str(e)}')