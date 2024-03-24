import uuid
from typing import List, Optional

from app_security import Session, sessions, users
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from pydantic import BaseModel, SecretStr

router = APIRouter()


class AuthCheck(BaseModel):
    token: str
    groups_needed: Optional[List[str]] = None


class AuthResponse(BaseModel):
    token: str


@router.post("/check", response_model=AuthResponse)
async def auth_check(request: Request, check: AuthCheck):
    print(await request.json())
    print(request.headers)
    # print(sessions)
    session = sessions.get(check.token)
    if session is None:
        logger.info("Existing session load failed | No session found")
        raise HTTPException(status_code=204)
    if session.is_valid() is not True:
        logger.info(f"Existing session load by '{sessions[check.token].username}' failed | Session expired")
        raise HTTPException(status_code=204)
    if session.sufficient_permissions(check.groups_needed) is not True:
        logger.info(f"Existing session load by '{sessions[check.token].username}' failed | insufficient permissions")
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    logger.info(f"Existing session load by {sessions[check.token].username} successful.")
    return AuthResponse(token=check.token)


class AuthRequest(BaseModel):
    username: str
    password: SecretStr
    groups_needed: Optional[List[str]] = None


@router.post("/token", response_model=AuthResponse)
async def auth_token(auth: AuthRequest):
    user = users.get(auth.username)
    if user is None:
        logger.info(f"Login attempt by '{auth.username}' failed | user doesn't exist")
        raise HTTPException(status_code=204, detail="Username or password is invalid")
    if user.is_valid(auth.password) is not True:
        logger.info(f"Login attempt by '{auth.username}' failed | invalid username or password")
        raise HTTPException(status_code=401, detail="Username or password is invalid")
    if user.sufficient_permissions(auth.groups_needed) is not True:
        logger.info(f"Login attempt by '{auth.username}' failed | Insufficient permissions")
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(username=auth.username, groups=user.groups)
    logger.info(f"Login attempt by '{sessions[session_id].username}' successful.")
    return AuthResponse(token=session_id)