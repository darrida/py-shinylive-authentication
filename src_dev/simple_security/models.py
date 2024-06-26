import secrets
from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel, SecretStr

SESSIONS_EXPIRE_MIN = 1


class User(BaseModel):
    username: str
    password: SecretStr
    groups: List[str] = None

    def is_valid(self, password: SecretStr) -> bool:
        if self.password.get_secret_value() != password.get_secret_value():
            print(f"Login attempted: {self.username} | Login status: FAILED | Action: NOT ACCESS")
            return False
        print(f"Login attempted: {self.username} | Login status: SUCCESS | Action: ALLOWED")
        return True
    
    def sufficient_permissions(self, required_groups: list = None) -> bool:
        return _sufficient_permissions(self.username, required_groups, self.groups)


class Session(BaseModel):
    username: str
    groups: List[str] = None
    expires: datetime = datetime.now() + timedelta(minutes=SESSIONS_EXPIRE_MIN)

    def is_valid(self) -> bool:
        if self.expires < datetime.now():
            print(f"Session loaded: {self.username} | Session status: EXPIRED | Action: NOT ACCESS")
            return False
        print(f"Session loaded: {self.username} | Session status: VALID | Action: ALLOWED")
        return True
    
    @staticmethod
    def create_id() -> str:
        return secrets.token_urlsafe(16)
    
    def refresh(self):
        self.expires = datetime.now() + timedelta(minutes=SESSIONS_EXPIRE_MIN)
        print(f"Session update: {self.username} | Action: Refreshed")

    def sufficient_permissions(self, required_groups: list = None) -> bool:
        return _sufficient_permissions(self.username, required_groups, self.groups)


def _sufficient_permissions(username: str, required_groups: list = None, user_groups: list = None) -> bool:
    if required_groups is not None and set(required_groups).issubset(user_groups) is False:
        print(f"User loaded: {username} | Permissions status: INVALID | Action: NOT ALLOWED")
        return False
    print(f"User loaded: {username} | Permissions status: VALID | Action: ALLOWED")
    return True