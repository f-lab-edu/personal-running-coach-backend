from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from schemas.models import LapData, StreamData, ActivityData
from infra.db.orm.models import ThirdPartyToken

class TrainingDataPort(ABC):
    """서드파티에서 훈련 데이터를 수집하는 포트 인터페이스"""
    
    @abstractmethod
    async def connect(self, auth_code: str) -> dict:
        """플랫폼에 연결. 플랫폼 토큰 받기"""
        ...
    
    @abstractmethod
    async def disconnect(self, user_id: UUID) -> bool:
        """플랫폼 연결 해제"""
        ...
    
    @abstractmethod    
    async def get_token_from_db(self, user_id:UUID) -> Optional[ThirdPartyToken]:
        """토큰 받기"""
        ...
    
    @abstractmethod
    async def fetch_activities(self, access_token:str, after_date: Optional[str] = None) -> List[ActivityData]:
        """서드파티 기간내 모든 훈련 활동 데이터 리스트 가져오기"""
        ...
        
    @abstractmethod
    async def fetch_activity_stream(self, access_token: str, activity_id:int) -> StreamData:
        """서드파티 훈련 활동의 스트림 데이터 가져오기"""
        ...

    @abstractmethod
    async def fetch_activity_lap(self, access_token: str, activity_id:int) -> List[LapData]:
        """서드파티 훈련 활동의 랩 데이터 가져오기"""
        ...
        
    @abstractmethod 
    async def is_token_expired(self, expires_at:int) -> bool:
        """서드파티토큰 만료 검증"""
        ...
        
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> dict:
        """플랫폼 토큰 갱신"""
        ...
