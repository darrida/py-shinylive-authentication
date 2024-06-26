from datetime import datetime

from pydantic import SecretStr

from .models import Session, User

users = {
    "username": User(username="username", password=SecretStr(value="password"), groups=["app1", "group1"]),
    "username2": User(username="username2", password=SecretStr(value="password2"), groups=["app2"]),
}


sessions = {"example_token": Session(username="example", expires=datetime.now())}