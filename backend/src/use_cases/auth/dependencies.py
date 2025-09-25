from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.storage.session import get_session
from uuid import UUID

from config.exceptions import CustomError, InternalError, TokenExpiredError, TokenInvalidError
from schemas.models import TokenPayload
from adapters import TokenAdapter
from infra.db.storage.repo import get_user_by_id

auth_scheme = HTTPBearer()
token_adapter = TokenAdapter()



async def get_test_user() -> TokenPayload:
    """테스트 유저 """
    return TokenPayload(
        user_id=UUID("7c311ca58af9472194f70fd4cf8f9b90"),
        exp=0,
        iat=0,
        token_type="access"
    )

async def get_current_user(
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> TokenPayload:
    """헤더에서 jwt 문자열 추출. 검증후 사용자 ID 추출"""
    try:
        return token_adapter.verify_access_token(access_cred.credentials)

    except CustomError:
        raise
    except Exception as e:
        raise InternalError(context="error get_current_user", original_exception=e)
    
async def validate_current_user(
    db:AsyncSession=Depends(get_session),
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> bool:
    """헤더의 jwt 사용자 ID validate"""
    try:
        payload = token_adapter.verify_access_token(access_cred.credentials)
        user = await get_user_by_id(user_id=payload.user_id, db=db) 
        if not user:
            raise TokenInvalidError(detail="invalid user token")
        return True
    except CustomError:
        raise
    except Exception as e:
        raise InternalError(context="error validate_current_user", original_exception=e)
    
async def get_current_header(
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> str:
    """헤더에서 jwt 문자열 추출"""
    try:
        return access_cred.credentials

    except Exception as e:
        raise InternalError(context="error get_current_header", original_exception=e)
    