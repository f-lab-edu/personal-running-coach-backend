from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.exceptions import TokenError
from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.storage.session import get_session

from schemas.models import TokenPayload
from adapters import TokenAdapter
from infra.db.storage.repo import get_user_by_id

auth_scheme = HTTPBearer()
token_adapter = TokenAdapter()

async def get_current_user(
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> TokenPayload:
    """헤더에서 jwt 문자열 추출. 검증후 사용자 ID 추출"""
    try:
        return token_adapter.verify_access_token(access_cred.credentials)
        
    except TokenError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
async def validate_current_user(
    db:AsyncSession=Depends(get_session),
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> bool:
    """헤더의 jwt 사용자 ID validate"""
    try:
        payload = token_adapter.verify_access_token(access_cred.credentials)
        user = await get_user_by_id(user_id=payload.user_id, db=db) 
        if not user:
            raise HTTPException(status_code=400, detail="invalid user token")
        return True
    except HTTPException:
        raise
    except TokenError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="error validating user token")

async def get_current_header(
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> str:
    """헤더에서 jwt 문자열 추출"""
    try:
        return access_cred.credentials
        
    except TokenError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
