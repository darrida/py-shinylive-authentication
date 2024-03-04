import uuid
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, SecretStr
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title='Sample Webserver and Auth Endpoint',
    redoc_url=None,
)

app.mount("/apps", StaticFiles(directory=Path(__file__).resolve().parent / "shinyapps", html=True), name="shinylive")

app.add_middleware(
        CORSMiddleware, 
        allow_origins=["http://localhost:8000", "http://localhsost:5000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


users = {
    "username": SecretStr(value="password"),
}


sessions = {
    "token": {
        "username": "", 
        "groups": []
    }
}


class AuthCheck(BaseModel):
    token: str
    groups_needed: List[str] = None


class AuthResponse(BaseModel):
    token: str


@app.post("/auth-check", response_model=AuthResponse)
async def auth_check(check: AuthCheck):
    if check.token not in sessions.keys():
        raise HTTPException(status_code=204, detail="No authenticated session found.")
    if not set(check.groups_needed).issubset(sessions[check.token]["groups"]):
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    return AuthResponse(token=check.token)


class AuthRequest(BaseModel):
    username: str
    password: SecretStr


@app.post("/auth-token", response_model=AuthResponse)
async def auth_token(auth: AuthRequest):
    if auth.username not in users.keys() or users.get(auth.username) != auth.password.get_secret_value():
        raise HTTPException(status_code=401, detail="Username or password is invalid")
    session_id = uuid.uuid4()
    sessions[session_id] = {"username": auth.username, "groups": ""}
    return AuthResponse(token=session_id)


uvicorn.run(
        app='src_webserver.main:app',
        port=8000,
    )