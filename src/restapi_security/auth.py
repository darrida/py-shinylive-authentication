from dataclasses import dataclass
from typing import List

from pydantic import SecretStr

from .shiny_api_calls import get_url

SESSIONS_EXPIRE_MIN = 2


@dataclass
class RestAPIAuth:
    required_permissions: List[str] = None
    
    async def get_auth(self, username: str, password: SecretStr) -> str:
        results = await get_url(
            url="http://localhost:8000/entsys/auth-token",
            headers={"Content-Type": "application/json"},
            body={"username": username, "password": password.get_secret_value(), "groups_needed": self.required_permissions},
            type="json",
            clone=True,
            method="POST"
        )
        status = int(results.status)
        if status in (401, 204):
            raise self.ShinyLiveAuthFailed
        if status in (403):
            raise self.ShinyLivePermissions
        return results.data["token"]

    async def check_auth(self, token: str) -> str:
        results = await get_url(
            url="http://localhost:8000/entsys/auth-check",
            headers={"Content-Type": "application/json"},
            body={"token": token, "groups_needed": self.required_permissions},
            type="json",
            clone=True,
            method="POST"
        )
        status = int(results.status)
        if status in (204, 401):
            raise self.ShinyLiveAuthExpired
        if status in (403):
            raise self.ShinyLivePermissions
        if status != 200:
            raise self.ShinyLiveAuthFailed
        return results.data["token"]

    class ShinyLiveAuthFailed(Exception):
        ...

    class ShinyLiveAuthExpired(Exception):
        ...

    class ShinyLivePermissions(Exception):
        ...