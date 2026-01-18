from sqlalchemy import select

from models import AsyncSession
from models.user import EmailCode

from datetime import datetime, timedelta


class EmailCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_email_code(self, email: str, code: str) -> EmailCode:
        async with self.session.begin():
            email_code = EmailCode(email=email, code=code)
            self.session.add(email_code)
            return email_code

    async def check_email_code(self, email:str, code:str) -> bool:
        async with self.session.begin():
            stmt = select(EmailCode).where(EmailCode.email == email, EmailCode.code == code)
            email_code:EmailCode | None = await self.session.scalar(stmt)
            if email_code is None:
                return False
            if (datetime.now() - email_code.created_time) > timedelta(minutes=10):
                return False
            return True



