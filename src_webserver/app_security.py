from pydantic import SecretStr

users = {
    "username": SecretStr(value="password"),
}


sessions = {
    "token": {
        "username": "", 
        "groups": []
    }
}