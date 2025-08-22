from abc import ABC, abstractmethod
from typing import Optional

class TrainingDataPort(ABC):
    """훈련 데이터를 수집하는 포트 인터페이스"""
    
    @abstractmethod
    async def connect(self, user_id: str, auth_code: str) -> dict:
        """플랫폼에 연결. 플랫폼 토큰 받기"""
        ...
    
    @abstractmethod
    async def disconnect(self, user_id: str) -> bool:
        """플랫폼 연결 해제"""
        ...
    
    @abstractmethod
    async def fetch_activities(self, user_id: str, after_date: Optional[str] = None) -> list:
        """훈련 활동 데이터 가져오기"""
        ...
    
    @abstractmethod
    async def refresh_token(self, user_id: str) -> dict:
        """플랫폼 토큰 갱신"""
        ...
