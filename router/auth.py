from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash

from models import Users
from database import SessionLocal

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a plain password."""
    return password_hash.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token with the provided data and expiration time."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Retrieve the current user based on the provided JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")
        role = payload.get("role")
        if username is None or user_id is None:
            raise credentials_exception
        return {"username": username, "id": user_id, "user_role": role}

    except InvalidTokenError as ex:
        raise credentials_exception from ex


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

class CreateUserRequest(BaseModel):
    """Request model for creating a new user account."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(..., min_length=1, max_length=50)
    phone_number: str = Field(..., min_length=6, max_length=10)

class Token(BaseModel):
    """Response model for authentication token."""
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

DbDependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest, db: DbDependency):
    """Create a new user account with the provided credentials."""

    user = Users(
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=get_password_hash(request.password),
        role=request.role,
        is_active=True,
        phone_number=request.phone_number
    )

    db.add(user)
    db.commit()

@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDependency):
    """Endpoint for user login to obtain authentication token."""
    user = db.query(Users).filter(Users.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    data = {"sub": user.username, "user_id": user.id, "role": user.role}
    access_token = create_access_token(
                                        data,
                                        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                                    )
    
    return {"access_token": access_token, "token_type": "bearer"}