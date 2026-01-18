from datetime import datetime

from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, DateTime
from pwdlib import PasswordHash

# 下载密码加密包
# pip install "pwdlib[argon2]"

password_hash = PasswordHash.recommended()

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    username: Mapped[str] = mapped_column(String(100))
    _password: Mapped[str] = mapped_column(String(200))

    def __init__(self, *args, **kwargs):
        password = kwargs.pop("password")
        super().__init__(*args, **kwargs)
        if password:
            self.password = password

    # 这种property + password.setter写法可以直接通过user.password的形式给
    # _password这个字段赋值，更优雅
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = password_hash.hash(value)

    def check_password(self, password):
        return password_hash.verify(password, self.password)

class EmailCode(Base):
    __tablename__ = "email_code"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(10))
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())