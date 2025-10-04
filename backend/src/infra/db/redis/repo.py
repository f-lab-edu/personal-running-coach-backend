from redis.asyncio import Redis
from config.exceptions import DBError



async def set_value(redisdb: Redis, k:str, v:str, ttl:int = None):
    """유저별 + 페이지별 etag 저장"""
    try:
        await redisdb.set(k, v, ex=ttl)
    except Exception as e:
        raise DBError(context=f"error set_value {k} {v}", original_exception=e)

async def get_value(redisdb: Redis, k:str) -> str | None:
    """유저별 + 페이지별 etag 조회"""
    try:
        return await redisdb.get(k)
    except Exception as e:
        raise DBError(context=f"error get_value {k}", original_exception=e)

async def delete_key(redisdb: Redis, k: str) -> int:
    """주어진 키를 삭제하고 삭제된 키 개수 반환"""
    try:
        deleted_count = await redisdb.delete(k)
        return deleted_count
    except Exception as e:
        raise DBError(context=f"error delete_key {k}", original_exception=e)