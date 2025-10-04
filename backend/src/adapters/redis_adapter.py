from redis.asyncio import Redis
from uuid import UUID
from ports.redis_port import RedisPort
from infra.db.redis import repo
from config.exceptions import InternalError, CustomError
from config.constants import ETAG_TTL_SEC

class RedisAdapter(RedisPort):
    def __init__(self, db:Redis):
        self.db = db

    
    ## 유저+페이지별 etag 키 생성
    def _etag_key(self, user_id: UUID, page: str) -> str:
        return f"user:{user_id}:page:{page}:etag"

    async def set_user_etag(self, user_id: UUID, page: str, etag: str):
        try:
            await repo.set_value(redisdb=self.db,
                                 k=self._etag_key(user_id=user_id, page=page),
                                 v=etag,
                                 ttl=ETAG_TTL_SEC
                                 )
        except CustomError:
            raise
        except Exception as e:
            InternalError(context=f"adapter set_user_etag {user_id} {page}", original_exception=e)

    
    async def get_user_etag(self,user_id: UUID, page: str) -> str | None:
        try:
            return await repo.get_value(redisdb=self.db,k=self._etag_key(user_id=user_id, page=page))
        except CustomError:
            raise
        except Exception as e:
            InternalError(context=f"adapter get_user_etag {user_id} {page}", original_exception=e)

    
    async def remove_user_etag(self, user_id: UUID, page: str):
        """사용자 페이지에 저장된 ETag를 삭제(만료)"""
        try:
            await repo.delete_key(
                redisdb=self.db,
                k=self._etag_key(user_id=user_id, page=page)
            )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(
                context=f"adapter remove_user_etag {user_id} {page}",
                original_exception=e
        )