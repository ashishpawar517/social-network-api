from pydantic import BaseModel
from typing import List, Optional


class PostBase(BaseModel):
    title: str
    body: str


class Post(PostBase):
    class Config:
        orm_mode = True


class User(BaseModel):
    name: str
    email: str
    password: str


class Title(BaseModel):
    title: str
    class Config:
        orm_mode = True


class UserSafe(BaseModel):
    name: str
    email: str
    posts: List[Post] = []

    class Config:
        orm_mode = True


class ShowPost(BaseModel):
    title: str
    body: str
    creator: UserSafe

    class Config:
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
