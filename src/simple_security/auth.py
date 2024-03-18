from dataclasses import dataclass
from typing import List, Optional

from pydantic import SecretStr

from .models import Session
from .storage import sessions, users

SESSIONS_EXPIRE_MIN = 2


@dataclass
class SimpleAuth:
    groups_needed: List[str] = None
    
    async def get_auth(self, username: str, password: SecretStr) -> str:
        user = users.get(username)
        # Does user exist?
        if user is None:
            raise self.ShinyLiveAuthFailed
        # Does password match?
        if user.is_valid(password) is False:
            raise self.ShinyLiveAuthFailed
        # Does user have sufficient permissions?
        if user.sufficient_permissions(self.groups_needed) is False:
            raise self.ShinyLivePermissions
        # Create token
        session_id = Session.create_id()
        sessions[session_id] = Session(username=username, groups=user.groups)
        return session_id

    async def check_auth(self, token: str) -> str:
        session = sessions.get(token)
        # Does session exist?
        if session is None:
            raise self.ShinyLiveAuthExpired
        # Is session expired?
        if session.is_valid() is False:
            raise self.ShinyLiveAuthExpired
        # Does user have sufficient permissions?
        if session.sufficient_permissions() is False:
            raise self.ShinyLivePermissions
        # Refresh token
        session.refresh()
        session_id = Session.create_id()
        sessions[session_id] = session.copy(deep=True)
        sessions.pop(token)
        # Remove old session
        return session_id

    class ShinyLiveAuthFailed(Exception):
        ...

    class ShinyLiveAuthExpired(Exception):
        ...

    class ShinyLivePermissions(Exception):
        ...