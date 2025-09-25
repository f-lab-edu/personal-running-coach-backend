from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from infra.db.storage.session import get_session
from interfaces.api.auth.auth_google import google_router
from interfaces.api.auth.auth_strava import strava_router
from schemas.models import LoginRequest, SignupRequest, LoginResponse
from use_cases.auth.auth import AuthHandler
from adapters import AccountAdapter, TokenAdapter
from config import constants
from config.exceptions import CustomError
from config.logger import get_logger

logger = get_logger(__file__)

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
    


@router.post("/login", response_model=LoginResponse)
async def login(request:LoginRequest, 
                auth_handler:AuthHandler=Depends(get_auth_handler)
                ):
    """로그인.
        parameter: Body(email, pwd)
        return: LoginResponse (token, user info)
    """
    try:
        token_response = await auth_handler.login(request.email, request.pwd)
        return token_response
    except CustomError as e:
        logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"login. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/signup")
async def signup(request:SignupRequest,
                 auth_handler:AuthHandler=Depends(get_auth_handler))->bool:
    """회원가입.
        parameter: Body(email, pwd, name)
        return: 회원가입 성공여부 (bool)
    """
    try:
        return await auth_handler.signup(request.email, request.pwd, request.name)
    except CustomError as e:
        logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"signup. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.post("/token", response_model=LoginResponse)
async def login_token(
    access_cred: HTTPAuthorizationCredentials = Depends(auth_scheme),
    auth_handler:AuthHandler=Depends(get_auth_handler)):
    """토큰 로그인
        header: access_token
        return: LoginResponse
    """
    try:
        access_token = access_cred.credentials
        return await auth_handler.login_token(access=access_token)
    except CustomError as e:
        logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"login_token. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    refresh_cred: HTTPAuthorizationCredentials = Depends(auth_scheme),
    auth_handler:AuthHandler=Depends(get_auth_handler)):
    """토큰 재발급
        header: refresh_token
        return: LoginResponse
    """
    try:
        refresh_token = refresh_cred.credentials
        return await auth_handler.refresh_token(access=refresh_token)
    except CustomError as e:
        logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"refresh. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    