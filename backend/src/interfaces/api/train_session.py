from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from adapters import StravaAdapter, TrainingAdapter, RedisAdapter
from infra.db.storage.session import get_session
from infra.db.redis.redis_client import get_redis, Redis
from use_cases.train_session.handle_train_session import TrainSessionHandler
from schemas.models import TokenPayload, TrainRequest, TrainSessionResponse
from use_cases.auth.dependencies import get_current_user, get_etag
from use_cases.auth.auth_strava import StravaHandler
from config.logger import get_logger
from config.exceptions import CustomError
logger = get_logger(__name__)

router = APIRouter(prefix="/trainsession", tags=['train-session'])


def get_handler(db:AsyncSession=Depends(get_session),
                redisdb:Redis=Depends(get_redis),
                )->TrainSessionHandler:
    data_adapter = StravaAdapter(db=db)
    training_adapter = TrainingAdapter(db=db)
    auth_handler = StravaHandler(db=db, adapter=data_adapter)
    redis_adapter = RedisAdapter(db=redisdb)
    return TrainSessionHandler(
        db_adapter=training_adapter,
        data_adapter=data_adapter,
        auth_handler=auth_handler,
        redis_adapter=redis_adapter
    )

# 스케줄 새로 로드
@router.get("/fetch-new-schedules")
async def fetch_schedule(
    date:Optional[int] = None,
    payload: TokenPayload = Depends(get_current_user),
    handler:TrainSessionHandler=Depends(get_handler)):
    try:
        return await handler.fetch_new_schedules(payload=payload, start_date=date)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"fetch_new_schedules. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 스케줄 불러오기
@router.get("/fetch-schedules", response_model=TrainSessionResponse)
async def fetch_schedule(
    date:Optional[int] = None,
    payload: TokenPayload = Depends(get_current_user),
    etag:str = Depends(get_etag),
    handler:TrainSessionHandler=Depends(get_handler),
    ):
    try:
        return await handler.get_schedules(payload=payload, etag=etag, start_date=date)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"fetch_schedule. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 스케줄 세부 정보
@router.get("/{session_id}")
async def fetch_schedule_detail(
    session_id:UUID,
    payload: TokenPayload = Depends(get_current_user),
    handler:TrainSessionHandler=Depends(get_handler)):
    try:
        return await handler.get_schedule_detail(payload=payload, session_id=session_id)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"fetch_schedule_detail. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.post("/upload")
async def upload_new_schedule(
    data:Optional[TrainRequest] = None,
    payload: TokenPayload = Depends(get_current_user),
    handler:TrainSessionHandler=Depends(get_handler)):
    try:
        return await handler.upload_new_schedule(payload=payload, session=data)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"upload session. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    