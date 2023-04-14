from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

app = FastAPI()

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


@app.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.get('/todos/{todo_id}')
async def get_todo_by_id(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        return HTTPException(status_code=404, detail="No such todo with these id")


@app.post('/')
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return {
        'status': 201,
        'transaction': "Successful"
    }


@app.put('/{todo_id}')
async def update_todo_by_id(todo_id: int, todo: Todo, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

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

@app.delete('/{todo_id}')
async def delete_todo_by_id(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo doesn't found")
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()

    return {
        'status': 200,
        'transaction': 'Successful'
    }