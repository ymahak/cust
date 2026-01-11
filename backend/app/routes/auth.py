from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.database.mongo import (
    create_user,
    verify_user,
    get_user_by_username
)
from app.auth.jwt import create_token, verify_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class SignupRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/signup")
async def signup(data: SignupRequest):
    existing_user = await get_user_by_username(data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = await create_user(
        data.username,
        data.password,
        data.role
    )

    return {
        "message": "User created successfully",
        "username": user["username"],
        "role": user["role"]
    }


@router.post("/login")
async def login(data: LoginRequest):
    user = await verify_user(data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token({
        "username": user["username"],
        "role": user["role"]
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    return {
        "username": payload["username"],
        "role": payload["role"]
    }
