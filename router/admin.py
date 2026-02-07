from sqlalchemy.orm import Session
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path

from starlette import status

from models import Todos
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
    
DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_todos(user: UserDependency, db: DbDependency):
    if not user or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return db.query(Todos).all()

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: UserDependency, db: DbDependency, todo_id: int = Path(gt=0)):
    if not user or user.get("user_role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    db.delete(todo)
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()