from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import httpx
from datetime import datetime, timezone


from ports.training_data_port import TrainingDataPort
from typing import Optional
from config.settings import strava, security



class StravaAdapter(TrainingDataPort):
    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def connect(self, auth_code: str) -> dict:
        """플랫폼에 연결. 스트라바 토큰 받기"""
        
        payload = {
            "client_id": strava.client_id,
            "client_secret": strava.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(strava.token_url, data=payload)
        
        response.raise_for_status()
        return response.json()
    
    async def disconnect(self, user_id: UUID) -> bool:
        """플랫폼 연결 해제"""
        ...
    
    async def fetch_activities(self, user_id: UUID, after_date: Optional[str] = None) -> list:
        """훈련 활동 데이터 가져오기"""
        ...
        
    async def is_token_expired(self, expires_at:int) -> bool:
        """토큰 만료 검증"""
        now = int(datetime.now(timezone.utc).timestamp())
        return expires_at <= now

    
    async def refresh_token(self, refresh_token: str) -> dict:
        """토큰 갱신"""
        payload = {
            "client_id": strava.client_id,
            "client_secret": strava.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(strava.token_url, data=payload)
        
        response.raise_for_status()
        return response.json()
