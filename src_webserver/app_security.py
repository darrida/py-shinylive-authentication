import secrets
from datetime import datetime, timedelta
from typing import List

from loguru import logger
from pydantic import BaseModel, SecretStr

SESSIONS_EXPIRE_MIN = 2


class User(BaseModel):
    username: str
    password: SecretStr
    groups: List[str] = None

    def is_valid(self, password: SecretStr) -> bool:
        if self.password.get_secret_value() != password.get_secret_value():
            return False
        return True
    
    def sufficient_permissions(self, required_groups: list = None) -> bool:
        return _sufficient_permissions(required_groups, self.groups)


class Session(BaseModel):
    username: str
    groups: List[str] = None
    expires: datetime = datetime.now() + timedelta(minutes=SESSIONS_EXPIRE_MIN)

    def is_valid(self) -> bool:
        if self.expires < datetime.now():
            return False
        return True
    
    @staticmethod
    def create_id() -> str:
        return secrets.token_urlsafe(16)
    
    def refresh(self):
        self.expires = datetime.now() + timedelta(minutes=SESSIONS_EXPIRE_MIN)
        logger.info(f"Session update: {self.username} | Action: Refreshed")

    def sufficient_permissions(self, required_groups: list = None) -> bool:
        return _sufficient_permissions(required_groups, self.groups)


def _sufficient_permissions(required_groups: list = None, user_groups: list = None) -> bool:
    if required_groups is not None and set(required_groups).issubset(user_groups) is False:
        return False
    return True

users = {
    "username": User(username="username", password=SecretStr(secret_value="password"), groups=["app1"]),
    "username2": User(username="username2", password=SecretStr(secret_value="password2"), groups=["app2"]),
}


sessions = {"example_token": Session(username="example", expires=datetime.now())}