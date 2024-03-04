import uuid
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, SecretStr

from .app_security import sessions, users

router = APIRouter()


class AuthCheck(BaseModel):
    token: str
    groups_needed: List[str] = None


class AuthResponse(BaseModel):
    token: str


@router.post("/auth-check", response_model=AuthResponse)
async def auth_check(check: AuthCheck):
    if check.token not in sessions.keys():
        raise HTTPException(status_code=204, detail="No authenticated session found.")
    if not set(check.groups_needed).issubset(sessions[check.token]["groups"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    return AuthResponse(token=check.token)


class AuthRequest(BaseModel):
    username: str
    password: SecretStr


@router.post("/auth-token", response_model=AuthResponse)
async def auth_token(auth: AuthRequest):
    if (
        auth.username not in users.keys() 
        or users.get(auth.username).get_secret_value() != auth.password.get_secret_value()
    ):
        raise HTTPException(status_code=401, detail="Username or password is invalid")
    session_id = uuid.uuid4()
    sessions[session_id] = {"username": auth.username, "groups": ""}
    return AuthResponse(token=session_id)