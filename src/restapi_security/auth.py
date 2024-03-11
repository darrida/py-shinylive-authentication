from dataclasses import dataclass
from typing import List

from pydantic import SecretStr

from .shiny_api_calls import get_url


class GeneralAuthException(Exception):
    ...


@dataclass
class RestAPIAuth:
    required_permissions: List[str] = None
    base_url: str = "http://localhost:8000"
    
    async def get_auth(self, username: str, password: SecretStr) -> str:
        results = await get_url(
            url=f"{self.base_url}/auth/token",
            headers={"Content-Type": "application/json"},
            body={"username": username, "password": password.get_secret_value(), "groups_needed": self.required_permissions},
            type="json",
            clone=True,
            method="POST"
        )
        status = int(results.status)
        if status in (401, 204,):
            raise self.ShinyLiveAuthFailed
        if status in (403,):
            raise self.ShinyLivePermissions
        if status not in (200,):
            print(status)
            raise self.ShinyLiveAuthExpired(f"Login for {username} failed due to an unknown reason. Status code: {status}")
        return results.data["token"]

    async def check_auth(self, token: str) -> str:
        results = await get_url(
            url=f"{self.base_url}/auth/check",
            headers={"Content-Type": "application/json"},
            body={"token": token, "groups_needed": self.required_permissions},
            type="json",
            clone=True,
            method="POST"
        )
        status = int(results.status)
        if status in (204, 401,):
            raise self.ShinyLiveAuthExpired
        if status in (403,):
            raise self.ShinyLivePermissions
        if status not in (200,):
            print(status)
            raise self.ShinyLiveAuthExpired(f"Authentication check failed due to an unknown reason. Status code: {status}")
        return results.data["token"]

    class ShinyLiveAuthFailed(Exception):
        ...

    class ShinyLiveAuthExpired(Exception):
        ...

    class ShinyLivePermissions(Exception):
        ...