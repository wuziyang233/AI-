# 梦开始的地方

1️⃣ alembic/

作用：数据库迁移（表结构版本管理）

用来管理数据库表结构的变更

常见命令：

```
alembic revision --autogenerate -m "xxx"
alembic upgrade head
```


里面一般包含：

versions/：每一次表结构变更的脚本

env.py：连接数据库、加载 models

👉 一句话：

不写业务逻辑，只负责“数据库结构怎么一步步演进”。

2️⃣ cores/

作用：项目核心基础能力（底层通用组件）

通常放这些东西：

数据库连接（Session、engine）

日志配置

安全相关（JWT、密码加密）

通用依赖（get_db 之类）

示例：

cores/
 ├── database.py
 ├── security.py
 ├── logger.py


👉 一句话：

所有模块都会用到的“地基代码”。

3️⃣ models/

作用：数据库 ORM 模型（SQLAlchemy Model）

每个文件 ≈ 一张表

定义字段、类型、索引、外键

示例：

```angular2html
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)

```

⚠️ 注意：

只描述表结构

不写业务逻辑

不写接口

👉 一句话：

数据库表在 Python 里的映射。

4️⃣ repository/

作用：数据库操作层（CRUD 封装）

这是很多人容易搞混的一层。

这里一般做什么？

对 models 的操作

封装查询逻辑

不关心 HTTP、不关心路由

示例：

```angular2html
def get_user_by_id(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```


👉 一句话：

“怎么查数据库”写在这里。

5️⃣ routers/

作用：API 路由层（FastAPI 路由）

对外暴露 HTTP 接口

处理请求/响应

调用 repository 或 service

示例：

```angular2html
@router.get("/users/{id}")
def get_user(id: int):
    return user_repo.get_user_by_id(db, id)
```



⚠️ 不要在这里直接写复杂数据库逻辑。

👉 一句话：

API 的入口，只做“接请求 + 返回结果”。

6️⃣ schemas/

作用：数据校验 & 序列化（Pydantic 模型）

请求参数校验

返回数据格式定义

和 models 不一样！

示例：
```angular2html
class UserCreate(BaseModel):
    name: str
```



常见用途：

POST / PUT 请求体

响应体格式约束

👉 一句话：

接口的数据“长什么样”。

7️⃣ settings/

作用：项目配置

一般包含：

数据库配置

环境变量

不同环境（dev / prod）

示例：

DATABASE_URL = "mysql://..."


👉 一句话：

所有“可配置”的东西。

🔁 一条完整调用链（非常重要）

一次 API 请求，通常流程是：

HTTP 请求
  ↓
routers      （接请求）
  ↓
schemas      （校验数据）
  ↓
repository  （查/写数据库）
  ↓
models      （表结构）
  ↓
数据库


| Python        | Java 更准确的对应        |
| ------------- | ------------------ |
| `models/`     | Entity             |
| `schemas/`    | **DTO（包含请求 / 响应）** |
| `routers/`    | Controller         |
| `repository/` | DAO / Repository   |
