from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.storage.session import get_session
from uuid import UUID

from config.logger import get_logger
from config.exceptions import CustomError, TokenInvalidError
from schemas.models import TokenPayload
from adapters import TokenAdapter
from infra.db.storage.repo import get_user_by_id

auth_scheme = HTTPBearer()
token_adapter = TokenAdapter()
logger = get_logger(__name__)


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

    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"get_current_user. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
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
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"validate_current_user. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
async def get_current_header(
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> str:
    """헤더에서 Authorization: Bearer jwt 문자열 추출"""
    try:
        return access_cred.credentials

    except Exception as e:
        logger.exception(f"get_current_header. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

async def get_etag(if_none_match: str | None = Header(None, alias="If-None-Match")) -> str | None:
    """
    클라이언트가 보낸 ETag를 헤더에서 추출
    FastAPI에서 자동으로 'If-None-Match' 헤더 매핑
    """
    try:
        if if_none_match is None:
            return None

        if not isinstance(if_none_match, str):
            raise HTTPException(status_code=400, detail="Invalid ETag header")

        return if_none_match
    except Exception as e:
        logger.exception(f"etag header. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")