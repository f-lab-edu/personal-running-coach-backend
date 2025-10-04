
        
from abc import ABC, abstractmethod
from redis.asyncio import Redis
from uuid import UUID


class RedisPort(ABC):

    @abstractmethod
    async def set_user_etag(self, user_id: UUID, page: str, etag: str):
        ...
    
    @abstractmethod
    async def get_user_etag(self, user_id: UUID, page: str) -> str | None:
        ...

    @abstractmethod
    async def remove_user_etag(self, user_id: UUID, page: str):
        ...