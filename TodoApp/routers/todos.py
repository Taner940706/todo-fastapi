import sys
sys.path.append("..")

from typing import Optional

from fastapi import Depends, HTTPException,APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# @app.get("/")
# async def create_database():
#     return {"Database": "Created"}

class Todo(BaseModel):
    title: str
    description: Optional[str]
    complete: bool


@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get('/todos/user')
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

@router.get('/todos/{todo_id}')
async def get_todo_by_id(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    else:
        return HTTPException(status_code=404, detail="No such todo with these id")


@router.post('/')
async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return {
        'status': 201,
        'transaction': "Successful"
    }


@router.put('/{todo_id}')
async def update_todo_by_id(todo_id: int, todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    if user is None:
        raise get_user_exception()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo doesn't found")

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return {
        'status': 200,
        'transaction': 'Successful'
    }

@router.delete('/{todo_id}')
async def delete_todo_by_id(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo doesn't found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()

    return {
        'status': 200,
        'transaction': 'Successful'
    }