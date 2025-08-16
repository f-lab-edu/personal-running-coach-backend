from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infra.db.storage.session import get_session
from interfaces.api.auth.auth_google import google_router
from interfaces.api.auth.auth_strava import strava_router
from schemas.models import TokenResponse, LoginRequest, SignupRequest, RefreshTokenRequest

from use_cases.auth.auth import AuthHandler
from adapters import AccountAdapter, TokenAdapter
from config import constants

router = APIRouter(prefix="/auth", tags=['auth'])
router.include_router(google_router, tags=None)
router.include_router(strava_router, tags=None)
auth_scheme = HTTPBearer()

def get_auth_handler(db:AsyncSession=Depends(get_session))->AuthHandler:
    return AuthHandler(
        account_adapter=AccountAdapter(db),
        token_adapter=TokenAdapter(
            access_token_exp=constants.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_exp=constants.REFRESH_TOKEN_EXPIRE_DAYS
            ),
        db=db
    )
    


@router.post("/login", response_model=TokenResponse)
async def login(request:LoginRequest, 
                auth_handler:AuthHandler=Depends(get_auth_handler)
                ):
    """로그인.
        parameter: Body(email, pwd)
        return: payload (access, refresh, exp ...)
    """
    
    token_response = await auth_handler.login(request.email, request.pwd)
    return token_response


@router.post("/signup")
async def signup(request:SignupRequest,
                 auth_handler:AuthHandler=Depends(get_auth_handler))->bool:
    """회원가입.
        parameter: Body(email, pwd, name)
        return: 회원가입 성공여부 (bool)
    """
    return await auth_handler.signup(request.email, request.pwd, request.name)
    
    

@router.post("/token", response_model=TokenResponse)
async def refresh(
    refresh_request:RefreshTokenRequest,
    access_cred: HTTPAuthorizationCredentials = Depends(auth_scheme),
    auth_handler:AuthHandler=Depends(get_auth_handler)):
    """토큰 로그인
        header: access_token
        body: refresh_token
        
        return: TokenResponse
    """
    access_token = access_cred.credentials
    refresh_token = refresh_request.refresh_token
    
    return await auth_handler.login_token(access=access_token, 
                                          refresh=refresh_token)
    
    