import random
import string
from typing import Annotated

import jwt
from aiosmtplib import SMTPResponseException
from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from fastapi_mail import FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, session

from dependencies import get_mail, get_session
from repository.user_repo import EmailCodeRepository, UserRepository
from schemas import ResponseOut
from schemas.user import UserRegisterIn, UserCreateSchema, UserLoginIn, UserLogOut, UserSchema
from cores.auth import AuthHandler

# 创建对戏那个（实例）
auth_handler = AuthHandler()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/code", response_model=ResponseOut)
async def get_code(
    email: Annotated[EmailStr, Query(...)],
    mail: FastMail = Depends(get_mail),
    session: AsyncSession = Depends(get_session)
):
    code = "".join(random.choices(string.digits, k=4))

    message = MessageSchema(
        subject="【AI起名】验证码",
        recipients=[str(email)],
        body=f"验证码是：{code}",
        subtype=MessageType.plain
    )

    repo = EmailCodeRepository(session)

    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        msg = str(e)
        # QQ 典型：QUIT/关闭阶段返回畸形响应行（含 \x00），但邮件已成功发送
        if e.code == -1 and ("Malformed SMTP response line" in msg or "\\x00" in msg):
            pass
        else:
            raise HTTPException(status_code=500, detail=f"邮件发送失败：{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"邮件发送失败：{e}")

    await repo.create_email_code(str(email), code)
    return ResponseOut()

@router.post("/register", response_model=ResponseOut)
async def register(
        data: UserRegisterIn,
        session: AsyncSession = Depends(get_session)
):
    user_repo = UserRepository(session)
    email_exist = await user_repo.email_exist(str(data.email))
    if email_exist:
        raise HTTPException(400, "邮箱已存在")

    code_repo = EmailCodeRepository(session)
    code_repo_match = await code_repo.check_email_code(str(data.email), str(data.code))
    if not code_repo_match:
        raise HTTPException(400, "邮箱或验证码错误")
    try:
        await user_repo.create_user(UserCreateSchema(
            email = data.email,
            username = data.username,
            password = data.password,
        ))
    except Exception as e:
        raise HTTPException(500, str(e))
    return ResponseOut()

@router.post("/login", response_model=UserLogOut)
async def login(
    data: UserLoginIn,
    session: AsyncSession = Depends(get_session)
):
    # 操作数据库，查一下用户是否存在
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(str(data.email))
    if not user:
        raise HTTPException(400, "用户不存在")
    check = user.check_password(data.password)
    if not check:
        raise HTTPException(400,"密码或邮箱错误")

    # 校验通过生成jwt
    token = auth_handler.encode_login_token(user_id=user.id)
    return {
        "user": user,
        "token": token["access_token"]
    }






