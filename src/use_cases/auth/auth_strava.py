from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import httpx
from datetime import datetime, timezone

from config.logger import get_logger
from config.settings import strava, security
from adapters import StravaAdapter
from infra.security import encrypt_token, TokenInvalidError
from infra.db.storage.third_party_token_repo import (
    get_third_party_token_by_user_id,
    create_third_party_token,
    update_third_party_token
)


logger = get_logger(__file__)


class StravaHandler:
    def __init__(self, db: AsyncSession, adapter: StravaAdapter, user=None):
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
        
        try:
            # 토큰 받기
            token = await self._get_token(code)

            # 토큰 암호화
            # refresh_token, access_token, 
            encrypted_access = encrypt_token(data=token.get("access_token"),
                                                key=security.encryption_key_strava,
                                                token_type="strava_access"
                                                )
            encrypted_refresh = encrypt_token(data=token.get("refresh_token"),
                                                key=security.encryption_key_strava,
                                                token_type="strava_refresh"
                                                )
            
            # 토큰 저장
            if not self.user:
                raise HTTPException(status_code=400, detail="User not authenticated")
            
            # expires_at을 현재 시간 + expires_in으로 계산
            expires_in = token.get("expires_at", 0)
            expires_at = int(datetime.now(timezone.utc).timestamp()) + expires_in
            
            # 기존 토큰이 있는지 확인
            existing_token = await get_third_party_token_by_user_id(
                user_id=self.user.id,
                provider="strava",
                db=self.db
            )
            
            if existing_token:
                # 기존 토큰이 있으면 업데이트
                await update_third_party_token(
                    user_id=self.user.id,
                    provider="strava",
                    access_token=encrypted_access,
                    refresh_token=encrypted_refresh,
                    expires_at=expires_at,
                    db=self.db
                )
            else:
                # 기존 토큰이 없으면 생성
                await create_third_party_token(
                    user_id=self.user.id,
                    provider="strava",
                    provider_user_id=str(token.get("athlete", {}).get("id", "")),
                    access_token=encrypted_access,
                    refresh_token=encrypted_refresh,
                    expires_at=expires_at,
                    db=self.db
                )
        
        except HTTPException as e:
            logger.exception(str(e))
            raise
        except TokenInvalidError as e:
            logger.exception(str(e))
            raise
        except Exception as e:
            logger.exception(str(e))
            raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")

        
        
        status = {"status": "ok",
                  "msg":"Strava connected successfully"
                  }
        
        return status