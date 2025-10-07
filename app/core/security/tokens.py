from datetime import datetime, UTC
from typing import Literal, Self
from app.conf import settings
from app.core.exceptions import InvalidToken, InvalidTokenType, ServiceError
from pydantic import BaseModel, Field, ConfigDict
import jwt

TokenType = Literal["access", "refresh"]


class _JWTToken(BaseModel):
    model_config = ConfigDict(extra="allow", from_attributes=True)
    max_age: int | None = Field(None, exclude=True)  # in seconds

    sub: str
    iat: datetime = Field(default_factory=lambda: datetime.now(UTC))
    exp: datetime | None = None
    aud: str | list[str] | None = None
    iss: str | list[str] | None = None
    jti: str | None = None

    @property
    def is_expired(self) -> bool:
        if self.exp is None:
            return False
        return datetime.now(UTC) >= self.exp

    def encode(self, **kwargs) -> str:
        payload = self.model_dump(exclude_none=True)
        return jwt.encode(
            payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM, **kwargs
        )

    @classmethod
    def decode(cls, token: str, **kwargs) -> Self:
        try:
            payload = jwt.decode(
                token,
                key=settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                **kwargs,
            )
        except jwt.ExpiredSignatureError:
            raise InvalidToken("Token has expired", title="Token expired")
        except jwt.DecodeError:
            raise InvalidToken("Token is invalid", title="Invalid token")
        except Exception as e:
            raise ServiceError(500, "Uknown error", "Uknown token error, cannot decode")
        return cls.model_validate(payload)


class AccessToken(_JWTToken):
    type_: TokenType = Field("access", alias="type")
    roles: list[str] = []
    permissions: list[str] = []

    @classmethod
    def decode(cls, token: str, **kwargs) -> Self:
        obj = super().decode(token, **kwargs)
        if obj.type_ != "access":
            raise InvalidTokenType(expected="access", received=obj.type_)
        return obj


class RefreshToken(_JWTToken):
    type_: TokenType = Field("refresh", alias="type")

    @classmethod
    def decode(self, token: str, **kwargs) -> Self:
        obj = super().decode(token, **kwargs)
        if obj.type_ != "refresh":
            raise InvalidTokenType(expected="refresh", received=obj.type_)
        return obj
