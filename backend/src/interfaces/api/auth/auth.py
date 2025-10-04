from fastapi import APIRouter, Body, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

from infra.db.storage.session import get_session
from interfaces.api.auth.auth_google import google_router
from interfaces.api.auth.auth_strava import strava_router
from schemas.models import LoginRequest, SignupRequest, LoginResponse, TokenPayload
from use_cases.auth.auth import AuthHandler
from adapters import AccountAdapter, TokenAdapter
from config import constants
from config.exceptions import CustomError
from use_cases.auth.dependencies import get_current_user
from config.logger import get_logger

logger = get_logger(__name__)

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
                response:Response,
                auth_handler:AuthHandler=Depends(get_auth_handler)
                ):
    """로그인.
        parameter: Body(email, pwd)
        return: LoginResponse (token, device_id, user_info, connected_info)
    """
    try:
        login_response = await auth_handler.login(request.email, request.pwd)

        # 리프레시 토큰을 쿠키로 전달
        response.set_cookie(
            key="refresh_token",
            value=login_response.token.refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=30 * 24 * 60 * 60
        )

        login_response.token.refresh_token = None
        return login_response        
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {e.original_exception}")
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
        if e.original_exception:
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
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"login_token. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    request:Request,
    refresh_cred: HTTPAuthorizationCredentials = Depends(auth_scheme),
    auth_handler:AuthHandler=Depends(get_auth_handler)):
    """토큰 재발급
        header: device_id
        httpOnly: refresh_token cookie 
        return: LoginResponse
    """
    try:
        device_id = UUID(refresh_cred.credentials)
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="no refresh token provided")
        return await auth_handler.refresh_token(refresh=refresh_token,
                                                device_id=device_id
                                                )
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"refresh. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.post("/logout")
async def logout(
    response: Response,
    device_id: UUID = Body(..., embed=True),  # 클라이언트가 로컬스토리지에 가지고 있는 device_id
    payload:TokenPayload = Depends(get_current_user),
    auth_handler:AuthHandler=Depends(get_auth_handler)
):

    try:
        response.delete_cookie("refresh_token", path="/")
        return await auth_handler.logout(user_id=payload.user_id, device_id=device_id)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"refresh. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")