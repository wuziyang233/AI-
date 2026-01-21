# 这个包下面写的东西可以理解成要返回的内容

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Annotated

usernameStr = Annotated[str, Field(min_length=3, max_length=20, description="用户名")]
passwordStr = Annotated[str, Field(min_length=6, max_length=20, description="密码")]


class UserRegisterIn(BaseModel):
    email: EmailStr
    username: usernameStr
    password: passwordStr
    confirm_password: passwordStr
    code: Annotated[str, Field(min_length=4, max_length=4, description="验证码")]

    @model_validator(mode="after")
    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("密码不一致")
        return self

class UserCreateSchema(BaseModel):
    email: EmailStr
    username: usernameStr
    password: passwordStr

class UserLoginIn(BaseModel):
    email: EmailStr
    password: passwordStr

class UserSchema(BaseModel):
    id: Annotated[int, Field(...)]
    email: EmailStr
    username: usernameStr

class UserLogOut(BaseModel):
    user: UserSchema
    token: str

