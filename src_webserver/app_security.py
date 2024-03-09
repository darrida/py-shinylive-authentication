from pydantic import SecretStr

users = {
    "username": SecretStr(value="password"),
    "username1": SecretStr(value="password1"),
}


sessions = {
    "token": {
        "username": "", 
        "groups": []
    }
}