from sqlalchemy.ext.asyncio import create_async_engine
from settings import DB_URI
# 3.创建会话工厂，在上面__init__.py文件基础上补全下面代码
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData



engine = create_async_engine(
    DB_URI,
    # 将输出所有执行 SQL 的日志（默认是关闭的）
    echo=True,
    # 连接池大小（默认是 5 个）
    pool_size=10,
    # 允许连接池最大的连接数（默认是 10 个）
    max_overflow=20,
    # 获取连接超时时间（默认是 30s）
    pool_timeout=10,
    # 连接回收时间（默认是 -1，代表永不回收）
    pool_recycle=3600,
    # 连接前是否预检查（默认为 False）
    pool_pre_ping=True,
)



AsyncSessionFactory = sessionmaker(
    # Engine 或者其子类对象（这里是 AsyncEngine）
    bind=engine,
    # Session 类的代替（默认是 Session 类）
    class_=AsyncSession,
    # 是否在查找之前执行 flush 操作（默认是 True）
    autoflush=True,
    # 是否在执行 commit 操作后 Session 就过期（默认是 True）
    expire_on_commit=False
)


# 定义命名约定的 Base 类
class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            # ix: index，索引
            "ix": "ix_%(column_0_label)s",
            # uq: unique，唯一约束
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            # ck: check，检查约束
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            # fk: foreign key，外键约束
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            # pk: primary key，主键约束
            "pk": "pk_%(table_name)s",
        }
    )

from . import user