from fastapi import FastAPI, Depends
from fastapi_mail import FastMail,MessageSchema,MessageType

from dependencies import get_mail

from aiosmtplib import SMTPResponseException

from routers.auth_router import router as auth_router


app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/mail/test")
async def mail_test(
        email: str,
        mail: FastMail = Depends(get_mail),
):
    message = MessageSchema(
        subject="hello",
        recipients=[email],
        body=f"Hello {email}",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        print("邮件发送成功")
    return {"message": "邮件发送成功"}

