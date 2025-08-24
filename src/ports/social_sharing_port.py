from abc import ABC, abstractmethod
from typing import Optional

class SocialSharingPort(ABC):
    """소셜 플랫폼에 콘텐츠를 공유하는 포트 인터페이스"""
    
    @abstractmethod
    async def connect(self, user_id: str, auth_code: str) -> bool:
        """플랫폼에 연결"""
        ...
    
    @abstractmethod
    async def disconnect(self, user_id: str) -> bool:
        """플랫폼 연결 해제"""
        ...
    
    @abstractmethod
    async def share_training_result(self, user_id: str, training_data: dict, message: Optional[str] = None) -> bool:
        """훈련 결과 공유"""
        ...
    
    @abstractmethod
    async def share_general_content(self, user_id: str, content: str, media_url: Optional[str] = None) -> bool:
        """일반 콘텐츠 공유"""
        ...
