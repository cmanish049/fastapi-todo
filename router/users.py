from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response

from starlette import status

from models import Users
from database import SessionLocal
from .auth import get_current_user, get_password_hash, verify_password

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

class User(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
    phone_number: str|None

class UserVersion(BaseModel):
    password: str
    new_password: str = Field(..., min_length=6)

class UserPhone(BaseModel):
    phone_number: str

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()
    
DbDependency = Annotated[Session, Depends(get_db)]
UserDependency = Annotated[dict, Depends(get_current_user)]

@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_current_user_info(user: UserDependency, db: DbDependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_data = db.query(Users).filter(Users.id == user.get("id")).first()
    return User(
        id=user_data.id,
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=user_data.is_active,
        role=user_data.role,
        phone_number=user_data.phone_number
    )

@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(password_data: UserVersion, user: UserDependency, db: DbDependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    user_data = db.query(Users).filter(Users.id == user.get("id")).first()
    
    # Verify current password
    if not user_data or not verify_password(password_data.password, user_data.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    user_data.hashed_password = get_password_hash(password_data.new_password)
    
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/users/update-phone', status_code=status.HTTP_204_NO_CONTENT)
def update_user_phone_number(phone_data: UserPhone, user: UserDependency, db: DbDependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    user_data = db.query(Users).filter(Users.id == user.get('id')).first()

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data.phone_number = phone_data.phone_number

    db.commit()
