from sqlalchemy.ext.asyncio import AsyncSession
import time
from uuid import UUID
import httpx
from datetime import datetime, timezone, timedelta


from ports.training_data_port import TrainingDataPort
from typing import Optional
from config.settings import strava, security
from infra.db.storage import third_party_token_repo as repo


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
        # 1. DB에서 액세스 토큰 가져오기
        access_token = await repo.get_third_party_token_by_user_id(
            db=self.db,
            provider="strava",
            user_id=user_id
        )
        
        if not access_token:
            return True  # 이미 끊겨 있음
        
        
        headers = {"Authorization": f"Bearer {access_token}"}
        url = strava.deauth_endpoint
        
        # strava 에서 연결 끊기        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, headers=headers)
            except httpx.HTTPError:
                pass
            
        # db 에서 토큰 삭제
        await repo.delete_third_party_token(
            db=self.db,
            provider="strava",
            user_id=user_id
        )
        
        return True
        
    
    async def fetch_activities(self, user_id:UUID, after_date: Optional[int] = None) -> list:
        """훈련 활동 데이터 가져오기
            user_id = 사용자 분류
            after_date = 시작날짜 (timestamp)
        """
        # get 액세스 토큰
        access_token = await repo.get_third_party_token_by_user_id(
                            db=self.db,
                            provider="strava",
                            user_id=user_id
                        )
        
        # 헤더 
        headers = {"Authorization": f"Bearer {access_token}"}
        
        url = strava.api_url + "athlete/activities"
        
        # 시작날짜 파라미터로
        if after_date is None:
            two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
            after_date = int(time.mktime(two_weeks_ago.timestamp()))
            
        params = {
            "after": after_date,
            "per_page": 100   # 최대 200까지 가능
        }
        
        # activities
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        
    
    async def fetch_activity_data(self, user_id: str, activity_id:int) -> list:


        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "keys": "heartrate,watts,cadence,distance,velocity_smooth,time",
            "key_by_type": "true"
        }
        
        url = strava.api_url + f"activities/{activity_id}/streams"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        
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
