from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    password: str
    salt: str
    admin: bool
