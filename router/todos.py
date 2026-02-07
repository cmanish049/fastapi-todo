from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path

from starlette import status

import models
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    tags=["Todos"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

dbDependency = Annotated[Session, Depends(get_db)]
userDependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100) 
    description: str = Field(min_length=1, max_length=250)
    priority: int = Field(gt=0, lt=11)
    completed: bool = Field(default=False)

@router.get("/todos", status_code=status.HTTP_200_OK)
def read_root(user: userDependency, db: dbDependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(user: userDependency, db: dbDependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    return todo


@router.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(request: TodoRequest, user: userDependency, db: dbDependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    new_todo = models.Todos(**request.model_dump(), owner_id=user.get("id"))

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo

@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(request: TodoRequest, user: userDependency, db: dbDependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    for key, value in request.model_dump().items():
        setattr(todo, key, value)

    db.commit()

    return

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: userDependency, db: dbDependency, todo_id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id, models.Todos.owner_id == user.get("id")).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return