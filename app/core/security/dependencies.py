from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from app.core.exceptions import InvalidToken
from .tokens import AccessToken, RefreshToken
from typing import Annotated


security = HTTPBearer(auto_error=False)


async def get_header_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials:
        if credentials.scheme.lower() == "bearer":
            return credentials.credentials
    else:
        raise InvalidToken("Authorization header is expected")
    raise InvalidToken("Provided token is invalid or expired")


async def get_access_token(token: str = Depends(get_header_token)) -> AccessToken:
    return AccessToken.decode(token)


async def get_refresh_token(token: str = Depends(get_header_token)) -> RefreshToken:
    return RefreshToken.decode(token)


AccessTokenDep = Annotated[AccessToken, Depends(get_access_token)]
RefreshTokenDep = Annotated[RefreshToken, Depends(get_refresh_token)]
