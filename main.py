from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path

from starlette import status

import models
from database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100) 
    description: str = Field(min_length=1, max_length=250)
    priority: int = Field(gt=0, lt=11)
    completed: bool = Field(default=False)

@app.get("/todos", status_code=status.HTTP_200_OK)
def read_root(db: db_dependency):
    return db.query(models.Todos).all()

@app.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    return todo


@app.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(request: TodoRequest, db: db_dependency):
    new_todo = models.Todos(**request.model_dump())

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo

@app.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(request: TodoRequest, db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    for key, value in request.model_dump().items():
        setattr(todo, key, value)

    db.commit()

    return

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return