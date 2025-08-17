from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from config.settings import google, security
from config.logger import get_logger
from schemas.models import LoginResponse
from adapters.account_adapter import AccountAdapter
from adapters.token_adapter import TokenAdapter
from infra.db.storage import repo
from infra.security import encrypt_token, decrypt_token, TokenInvalidError

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
                 token_adapter:TokenAdapter,
                 db:AsyncSession
                 ):
        self.db = db
        self.token_url = google.token_url
        self.account_adapter = account_adapter
        self.token_adapter = token_adapter
    
    
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
    
    
    
    
    async def handle_login(self, auth_code: str) -> LoginResponse:
        """
        구글 로그인.
        구글 authorization code 를 받아 엑세스 토큰 요청.
        엑세스 토큰 (json) 에서 id_token 추출.
        id_token 검증 후 유저정보 추출. 
        기존 db에 리프레시토큰이 존재하는지 확인
        유저정보로 로그인
        return: LoginResponse
        """
        try:
            # 1. google authcode 에서 access token 요청
            token_response = await self._get_access_token(auth_code)
            # response from auth_code
            # ['access_token', 'expires_in', 'refresh_token', 
            # 'scope', 'token_type', 'id_token']
            id_token_jwt = token_response.get("id_token")
            
            if not id_token_jwt:
                raise HTTPException(status_code=400, detail="No ID token received")
            

            
            
            # 2. ID 토큰 검증 및 사용자 정보 파싱
            
            id_info = id_token.verify_oauth2_token(
                id_token_jwt,
                google_requests.Request(),
                google.client_id
            )

            email = id_info.get("email")
            name = id_info.get("name")
            
            if not email:
                raise HTTPException(status_code=400, detail="Invalid google account")
            
            # 3. 로그인. 신규로그인시 유저 생성
            
            account_response = await self.account_adapter.provider_login(
                email=email, 
                provider="google", 
                name=name
            )

            user_id = str(account_response.id)
            
            # 액세스 토큰 생성
            access_token = self.token_adapter.create_access_token(user_id=user_id).access_token
            
            
            # 4. 기존 리프레시 토큰 있는지 확인
            existing_token = await repo.get_refresh_token(user_id=account_response.id,
                                                        db=self.db
                                                        )
            if existing_token:
                refresh_token = decrypt_token(existing_token,
                                        key=security.encryption_key_refresh)

            else:
                # 5. 새 리프레시 토큰 발급
                refresh_token = self.token_adapter.create_refresh_token(user_id=user_id).refresh_token
                
                # 리프레시 토큰 암호화
                encrypted = encrypt_token(data=refresh_token,
                                        key=security.encryption_key_refresh,
                                        token_type="account_refresh"
                                        )
            
                # 리프레시 토큰 저장
                await repo.add_refresh_token(
                    user_id=account_response.id, token=encrypted, db=self.db
                )        
            
            
            # 토큰 리턴
            return LoginResponse(
                id=account_response.id,
                email=account_response.email,
                name=account_response.name,
                access_token=access_token,
                refresh_token=refresh_token,
            )

        except HTTPException:
            raise
        except TokenInvalidError as e:
            logger.exception(str(e))
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logger.exception(str(e))
            raise HTTPException(status_code=500, detail="internal server error")
            