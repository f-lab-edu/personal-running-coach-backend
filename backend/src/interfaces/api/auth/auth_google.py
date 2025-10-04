"""
구글 oauth2 로그인 흐름
1. 클라이언트가 /login 호출
2. 구글 로그인 페이지로 리다이렉트
3. 클라이언트가 구글 아이디로 로그인
4. 구글이 프론트 주소로 리다이렉트
5. 프론트에서 code 받아서 다시 callback 호출
6. 로그인 처리 후 토큰 반환 

"""
from fastapi import APIRouter, HTTPException, Depends, Body, Response
from starlette.responses import RedirectResponse
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.storage.session import get_session
from schemas.models import LoginResponse
from adapters.account_adapter import AccountAdapter
from adapters.token_adapter import TokenAdapter
from use_cases.auth.oauth_google import GoogleHandler
from config.settings import google
from config.exceptions import CustomError
from config.logger import get_logger

logger = get_logger(__name__)

google_router = APIRouter(prefix="/google", tags=['auth-google'])

def get_handler(db:AsyncSession=Depends(get_session))->GoogleHandler:
    return GoogleHandler(
        account_adapter=AccountAdapter(db),
        token_adapter=TokenAdapter(),
        db=db
    )

@google_router.get("/login")
async def login_with_google():
    try:
        params = {
            "client_id": google.client_id,
            "redirect_uri": google.redirect_uri, ## 프론트 콜백 uri
            "response_type": "code", 
            "scope": google.scope,
            "access_type": "offline",  # online 
            "prompt": "consent",
        }
        url = f"{google.auth_endpoint}?{urllib.parse.urlencode(params)}"
        return RedirectResponse(url)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"login_with_google. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@google_router.post("/callback", response_model=LoginResponse)
async def google_callback(response:Response,
                        code:str = Body(..., embed=True),  
                        google_handler:GoogleHandler = Depends(get_handler)):
    if not code:
        raise HTTPException(status_code=400, detail="missing code")
    try:
        login_res = await google_handler.handle_login(auth_code=code)

        response.set_cookie(
            key="refresh_token",
            value=login_res.token.refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=30 * 24 * 60 * 60
        )
        login_res.token.refresh_token = None
        return login_res
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"google callback. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")