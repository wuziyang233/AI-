# core/auth.py
import jwt
from datetime import datetime
from enum import Enum
from threading import Lock

import settings
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

# 依赖：pip install pyjwt==2.10.1


class SingletonMeta(type):
    """Thread-safe Singleton MetaClass."""
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class TokenTypeEnum(int, Enum):
    ACCESS_TOKEN = 1
    REFRESH_TOKEN = 2


class AuthHandler(metaclass=SingletonMeta):
    """
    用法：
    - 登录成功后：AuthHandler().encode_login_token(user_id)
    - 受保护接口鉴权：
        user_id = Depends(AuthHandler().auth_wrapper)
      或：
        user_id = Depends(AuthHandler().auth_wrapper)  # 推荐写法
    """
    security = HTTPBearer()  # Authorization: Bearer {token}

    def __init__(self):
        self.secret = settings.JWT_SECRET_KEY

    def _encode_token(self, user_id: int, token_type: TokenTypeEnum) -> str:
        """
        payload:
        - iss: user_id（这里用字符串保存，decode 时再转 int）
        - sub: token type（PyJWT 要求 sub 必须是字符串）
        - exp: 过期时间（timestamp）
        """
        payload = {
            "iss": str(user_id),
            "sub": str(int(token_type.value)),  # ✅ sub 必须是 string
        }

        if token_type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES
        else:
            exp = datetime.now() + settings.JWT_REFRESH_TOKEN_EXPIRES

        payload["exp"] = int(exp.timestamp())

        return jwt.encode(payload, self.secret, algorithm="HS256")

    def encode_login_token(self, user_id: int) -> dict:
        """登录时返回 access_token + refresh_token"""
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def encode_update_token(self, user_id: int) -> dict:
        """刷新后只返回新的 access_token（常见做法）"""
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        return {"access_token": access_token}

    def decode_access_token(self, token: str) -> int:
        """
        ACCESS TOKEN: 不可用（过期，或有问题），都用 403
        返回 user_id
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])

            # ✅ sub 是 string，所以对比也用 string
            if payload.get("sub") != str(int(TokenTypeEnum.ACCESS_TOKEN.value)):
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Token类型错误！",
                )

            iss = payload.get("iss")
            if iss is None:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Token缺少iss字段！",
                )

            return int(iss)

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Access Token已过期",
            )
        except jwt.InvalidTokenError as e:
            # 开发期排查用：看清楚到底是啥原因（签名不匹配/格式不对等）
            # 生产环境建议去掉 print，改为日志
            print("JWT InvalidTokenError:", repr(e))
            print("Using secret:", self.secret)
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Access Token不可用: {e}",
            )

    def decode_refresh_token(self, token: str) -> int:
        """
        REFRESH TOKEN: 不可用（过期，或有问题），都用 401
        返回 user_id
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])

            if payload.get("sub") != str(int(TokenTypeEnum.REFRESH_TOKEN.value)):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Token类型错误！",
                )

            iss = payload.get("iss")
            if iss is None:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Token缺少iss字段！",
                )

            return int(iss)

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Refresh Token已过期",
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Refresh Token不可用: {e}",
            )

    def auth_wrapper(
        self,
        auth: HTTPAuthorizationCredentials = Security(security),
    ) -> int:
        """
        FastAPI 依赖注入用：
            user_id = Depends(AuthHandler().auth_wrapper)
        """
        return self.decode_access_token(auth.credentials)


# 你也可以在别处直接导入这个实例使用
auth_handler = AuthHandler()
