from sqlalchemy.ext.asyncio import AsyncSession


from src.ports.training_data_port import TrainingDataPort
from typing import Optional
from config.settings import strava


class StravaAdapter(TrainingDataPort):
    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def connect(self, user_id: str, auth_code: str) -> bool:
        """플랫폼에 연결"""
        ...
    
    async def disconnect(self, user_id: str) -> bool:
        """플랫폼 연결 해제"""
        ...
    
    async def fetch_activities(self, user_id: str, after_date: Optional[str] = None) -> list:
        """훈련 활동 데이터 가져오기"""
        ...
    
    async def refresh_token(self, user_id: str) -> bool:
        """토큰 갱신"""
        ...