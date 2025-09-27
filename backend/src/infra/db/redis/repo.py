from redis.asyncio import Redis
from uuid import UUID


## 유저+페이지별 etag 키 생성
def _etag_key(user_id: UUID, page: str) -> str:
    return f"user:{user_id}:page:{page}:etag"

async def set_user_etag(redisdb: Redis, user_id: UUID, page: str, etag: str):
    """유저별 + 페이지별 etag 저장"""
    await redisdb.set(_etag_key(user_id, page), etag)

async def get_user_etag(redisdb: Redis, user_id: UUID, page: str) -> str | None:
    """유저별 + 페이지별 etag 조회"""
    return await redisdb.get(_etag_key(user_id, page))