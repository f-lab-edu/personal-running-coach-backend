from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx

from config.settings import google
from config.logger import get_logger
from schemas.models import TokenResponse
from adapters.account_adapter import AccountAdapter
from adapters.token_adapter import TokenAdapter
from use_cases.auth.auth import AuthHandler

logger = get_logger(__file__)

# google_auth_oauthlib, google_oauth2 등 라이브러리 사용
# https://developers.google.com/identity/protocols/oauth2?hl=ko
# https://ahn3330.tistory.com/166
# https://m.blog.naver.com/nan17a/222182983858


class GoogleHandler:
    """
    구글 핸들러.

    """
    def __init__(self, account_adapter:AccountAdapter,
                 token_adapter:TokenAdapter):
        self.token_url = google.token_url
        self.account_adapter = account_adapter
        self.token_adatper = token_adapter
    
    
    async def _get_access_token(self, code:str)->dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "code": code,
                    "client_id": google.client_id,
                    "client_secret": google.client_secret,
                    "redirect_uri": google.redirect_uri,
                    "grant_type": "authorization_code"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        return response.json()
    
    
    
    
    async def handle_login(self, auth_code: str) -> TokenResponse:
        """
        구글 로그인.
        구글 authorization code 를 받아 엑세스 토큰 요청.
        엑세스 토큰 (json) 에서 id_token 추출.
        id_token 검증 후 유저정보 추출. 유저정보로 로그인
        
        return: TokenResponse
        """
        
         # 1. google authcode 에서 access token 요청
        token_response = await self._get_access_token(auth_code)
        # response from auth_code
        # ['access_token', 'expires_in', 'refresh_token', 
        # 'scope', 'token_type', 'id_token']
        id_token_jwt = token_response.get("id_token")
        
        if not id_token_jwt:
            raise HTTPException(status_code=400, detail="No ID token received")
        

        
        
        # 2. ID 토큰 검증 및 사용자 정보 파싱
        try:
            id_info = id_token.verify_oauth2_token(
                id_token_jwt,
                google_requests.Request(),
                google.client_id
            )
        except Exception as e:
            logger.exception(f"invalid id token: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid ID token: {str(e)}")

        email = id_info.get("email")
        name = id_info.get("name")  # Google provides name
        
        if not email:
            raise HTTPException(status_code=400, detail="Invalid google account")
        
        # 3. Login or create user account
        try:
            account_response = await self.account_adapter.provider_login(
                email=email, 
                provider="google", 
                name=name
            )
        except Exception as e:
            logger.exception(f"Error in provider login: {e}")
            raise HTTPException(status_code=500, detail="Failed to process OAuth login")
        
        # 4. Create and return access token
        access_token = self.token_adatper.create_access_token(user_id=str(account_response.id))
        refresh_token = self.token_adatper.create_refresh_token(user_id=str(account_response.id))
        
        return TokenResponse(
            access_token=access_token.access_token,
            refresh_token=refresh_token.refresh_token,
            exp=access_token.exp
        )

    
