from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError
from config.settings import redisdb
import os
import fakeredis
"""
모듈 레벨 싱글톤 Redis
로컬 환경시 fakeredis 반환
"""
RUN_ENV = os.getenv("RUN_ENV", "local")
FAKE_REDIS = RUN_ENV == "local"
print(FAKE_REDIS)

redis_instance: Redis | None = None

async def init_redis():
    """
    애플리케이션 시작 시 Redis 연결 초기화
    """
    global redis_instance
    if redis_instance is None:
        if FAKE_REDIS:
            redis_instance = fakeredis.aioredis.FakeRedis(decode_responses=True)
        else:
            try:
                redis_instance = Redis(
                    host=redisdb.host,
                    port=redisdb.port,
                    decode_responses=True,
                    max_connections=300,
                )
                # 필요하면 TTL 만료 이벤트 구독 등 여기서 추가 설정
            except (ConnectionError, RedisError) as e:
                raise RuntimeError(f"Redis 초기화 실패 {e}") from e


async def close_redis():
    """
    애플리케이션 종료 시 Redis 연결 종료
    """
    global redis_instance
    if redis_instance is not None:
        await redis_instance.close()
        redis_instance = None


def get_redis() -> Redis:
    """
    이미 초기화된 Redis 인스턴스를 반환
    (init_redis() 이후에만 안전하게 호출 가능)
    """
    if redis_instance is None:
        raise RuntimeError("Redis가 초기화되지 않았습니다. init_redis() 먼저 실행하세요.")
    return redis_instance