# core/auth.py
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
from enum import Enum
import settings
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from threading import Lock


# pyjwt: pip install pyjwt==2.10.1


class SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """
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
    - 受保护接口鉴权：user_id = AuthHandler().auth_wrapper(credentials)
      其中 credentials 来自 Security(AuthHandler().security)
    """
    security = HTTPBearer()  # Authorization: Bearer {token}

    secret = settings.JWT_SECRET_KEY

    def _encode_token(self, user_id: int, type: TokenTypeEnum):
        """
        payload:
        - iss: user_id
        - sub: token type (access/refresh)
        - exp: 过期时间（timestamp）
        """
        payload = dict(
            iss=user_id,
            sub=int(type.value),
        )
        to_encode = payload.copy()

        if type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.now() + settings.JWT_ACCESS_TOKEN_EXPIRES
        else:
            exp = datetime.now() + settings.JWT_REFRESH_TOKEN_EXPIRES

        to_encode.update({"exp": int(exp.timestamp())})

        return jwt.encode(to_encode, self.secret, algorithm="HS256")

    def encode_login_token(self, user_id: int):
        """
        登录时返回 access_token + refresh_token
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        login_token = dict(
            access_token=f"{access_token}",
            refresh_token=f"{refresh_token}",
        )
        return login_token

    def encode_update_token(self, user_id: int):
        """
        刷新后只返回新的 access_token（常见做法）
        """
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        update_token = dict(
            access_token=f"{access_token}",
        )
        return update_token

    def decode_access_token(self, token: str) -> int:
        """
        ACCESS TOKEN: 不可用（过期，或有问题），都用 403
        返回 user_id
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            if payload.get("sub") != int(TokenTypeEnum.ACCESS_TOKEN.value):
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Token类型错误！",
                )
            return int(payload.get("iss"))
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Access Token已过期",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Access Token不可用",
            )

    def decode_refresh_token(self, token: str) -> int:
        """
        REFRESH TOKEN: 不可用（过期，或有问题），都用 401
        返回 user_id
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            if payload.get("sub") != int(TokenTypeEnum.REFRESH_TOKEN.value):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Token类型错误！",
                )
            return int(payload.get("iss"))
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Refresh Token已过期",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Refresh Token不可用",
            )

    def auth_wrapper(
        self,
        auth: HTTPAuthorizationCredentials = Security(security),
    ) -> int:
        """
        FastAPI 依赖注入用：
        user_id = Depends(AuthHandler().auth_wrapper)
        或者：
        user_id = AuthHandler().auth_wrapper()
        """
        return self.decode_access_token(auth.credentials)
