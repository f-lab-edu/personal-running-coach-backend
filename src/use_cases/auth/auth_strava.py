from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import httpx

from config.logger import get_logger
from config.settings import strava, security
from adapters import StravaAdapter
from infra.security import encrypt_token, TokenInvalidError



logger = get_logger(__file__)


class StravaHandler:
    def __init__(self, user, db: AsyncSession, adapter: StravaAdapter):
        self.user = user
        self.db = db
        self.strava_adapter = adapter


    async def _get_token(self, code:str)->dict:
        """스트라바 토큰 받기"""
        payload = {
            "client_id": strava.client_id,
            "client_secret": strava.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(strava.token_url, data=payload)
        
        response.raise_for_status()
        return response.json()
    
        
    async def connect(self, code:str)->bool:
        """스트라바 토큰 저장. """
        
        # 토큰 받기
        token = await self._get_token(code)
    
        # TODO: 토큰 암호화
        # refresh_token, access_token, 
        try:
            encrypted_access = encrypt_token(data=token.get("access_token"),
                                             key=security.encryption_key_strava,
                                             token_type="strava_access"
                                             )
            encrypted_refresh = encrypt_token(data=token.get("refresh_token"),
                                              key=security.encryption_key_strava,
                                              token_type="strava_refresh"
                                              )
        
        # TODO: 토큰 저장
        
        
        
        except HTTPException:
            raise
        except TokenInvalidError:
            raise
        except Exception as e:
            logger.exception(str(e))
            raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")

        
        
        status = {"status": "ok",
                  "msg":"Strava connected successfully"
                  }
        
        return status