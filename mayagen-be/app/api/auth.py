from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..core import security
from ..database import get_session
from ..models import User
from .deps import get_current_user
from ..helpers import api_response_helper as responses

from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

router = APIRouter()

@router.post("/register")
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    # Check existing user
    result = await session.execute(select(User).where((User.username == request.username) | (User.email == request.email)))
    if result.scalars().first():
        return responses.api_error(
            status_code=400,
            message="Registration Failed",
            error="Username or email already registered"
        )
    
    # Create User
    db_user = User(
        username=request.username,
        email=request.email,
        hashed_password=security.get_password_hash(request.password)
    )
    session.add(db_user)
    await session.commit()
    return responses.api_success(
        status_code=201,
        message="User registered successfully",
        data={"username": request.username}
    )

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # Authenticate User
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        return responses.api_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Login Failed",
            error="Incorrect username or password"
        )
        
    # Create Token
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return responses.api_success(
        message="Login Successful",
        data={"access_token": access_token, "token_type": "bearer"}
    )

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return responses.api_success(
        message="User Profile Retrieved",
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat()
        }
    )
