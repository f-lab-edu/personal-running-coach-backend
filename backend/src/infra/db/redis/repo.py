from redis.asyncio import Redis
from config.exceptions import DBError



async def set_value(redisdb: Redis, k:str, v:str):
    """유저별 + 페이지별 etag 저장"""
    try:
        await redisdb.set(k, v)
    except Exception as e:
        raise DBError(context=f"error set_value {k} {v}", original_exception=e)

async def get_value(redisdb: Redis, k:str) -> str | None:
    """유저별 + 페이지별 etag 조회"""
    try:
        return await redisdb.get(k)
    except Exception as e:
        raise DBError(context=f"error get_value {k}", original_exception=e)