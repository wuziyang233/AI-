from sqlalchemy.ext.asyncio import AsyncSession

from cores.mail import create_mail_instance
from fastapi_mail import FastMail

from models import AsyncSessionFactory


async def get_mail() -> FastMail:
    return create_mail_instance()

# 操作数据库，邮件应该放到redis里才合理
async def get_session() -> AsyncSession:
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()


