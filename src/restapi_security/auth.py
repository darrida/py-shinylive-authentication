import json
import sys
from dataclasses import dataclass
from typing import Optional

from pydantic import SecretStr

# from .shiny_api_calls import get_url

if "pyodide" in sys.modules:
    from pyodide import http
else:
    from .pyodide_wrapper import http


class GeneralAuthException(Exception):
    ...


@dataclass
class RestAPIAuth:
    groups_needed: Optional[list] = None
    base_url: str = "http://localhost:8000"
    
    async def get_auth(self, username: str, password: SecretStr) -> str:
        response = await http.pyfetch(
            url=f"{self.base_url}/auth/token",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"username": username, "password": password.get_secret_value(), "groups_needed": self.groups_needed}),
            method="POST"
        )
        status = int(response.status)
        if status in (401, 204,):
            raise self.ShinyLiveAuthFailed
        if status in (403,):
            raise self.ShinyLivePermissions
        if status not in (200,):
            print(status)
            raise self.ShinyLiveAuthExpired(f"Login for {username} failed due to an unknown reason. Status code: {status}")
        data = await response.json()
        return data["token"]

    async def check_auth(self, token: str) -> str:
        response = await http.pyfetch(
            url=f"{self.base_url}/auth/check",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"token": token, "groups_needed": self.groups_needed}),
            method="POST"
        )
        status = int(response.status)
        if status in (204, 401,):
            raise self.ShinyLiveAuthExpired
        if status in (403,):
            raise self.ShinyLivePermissions
        if status not in (200,):
            print(status)
            raise self.ShinyLiveAuthExpired(f"Authentication check failed due to an unknown reason. Status code: {status}")
        data = await response.json()
        return data["token"]

    class ShinyLiveAuthFailed(Exception):
        ...

    class ShinyLiveAuthExpired(Exception):
        ...

    class ShinyLivePermissions(Exception):
        ...