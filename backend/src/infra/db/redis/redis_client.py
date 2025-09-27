from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError
from config.settings import redisdb

"""
모듈 레벨 싱글톤 Redis
"""

redis_instance: Redis | None = None

async def init_redis():
    """
    애플리케이션 시작 시 Redis 연결 초기화
    """
    global redis_instance
    if redis_instance is None:
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

class RedisRepo:
    """Redis 싱글톤 객체"""
    _instance = None
    
    @classmethod
    async def get_instance(cls)-> Redis:
        if cls._instance is None:
            try:
                cls._instance = Redis(
                    host=redisdb.host,
                    port=redisdb.port,
                    decode_responses=True,
                    max_connections=300
                )
                ## TTL 만료 이벤트 설정
            except (ConnectionError, RedisError) as e:
                raise RuntimeError(f"Redis 초기화 실패 {e}") from e
        return cls._instance
    
    
async def get_redis():
    return await RedisRepo.get_instance()
######################################################

"""
모듈레벨 싱글톤 방식
lifespan 에서 redis 초기화 후 get_redis_sync 함수로 객체 반환
"""
redis_instance = None

async def init_redis():
    global redis_instance
    if redis_instance is None:
        redis_instance = await RedisRepo.get_instance()
        
def get_redis_sync():
    return redis_instance
    