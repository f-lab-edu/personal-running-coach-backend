from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.exceptions import TokenError

from schemas.models import TokenPayload
from adapters import TokenAdapter

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

async def get_current_header(
    access_cred:HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> str:
    """헤더에서 jwt 문자열 추출"""
    try:
        return access_cred.credentials
        
    except TokenError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
