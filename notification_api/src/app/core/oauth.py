from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from starlette import status

from app.core.config import settings

bearer = HTTPBearer()


class AccessTokenData(BaseModel):
    """Модель полей access-токена"""

    sub: UUID
    is_admin: bool = False
    is_staff: bool = False
    roles: list[str] = []


async def decode_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> AccessTokenData:
    if credentials:
        if not credentials.scheme == 'Bearer':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authentication scheme.'
            )
        try:
            decoded_token = jwt.decode(
                token=credentials.credentials,
                key=settings.AUTH.SECRET_KEY,
                algorithms=[settings.AUTH.ALGORITHM],
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid token or expired token.',
            )
        try:
            return AccessTokenData(**decoded_token)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token payload',
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization code.'
        )


async def get_user_id(token_data: AccessTokenData = Depends(decode_jwt)) -> UUID:
    return token_data.sub
