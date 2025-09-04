from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters import StravaAdapter
from infra.db.storage.session import get_session
from use_cases.train_session.handle_train_session import TrainSessionHandler
from schemas.models import TokenPayload
from use_cases.auth.dependencies import get_current_user
from use_cases.auth.auth_strava import StravaHandler


router = APIRouter(prefix="/trainsession", tags=['train-session'])


def get_handler(db:AsyncSession=Depends(get_session))->TrainSessionHandler:
    adapter = StravaAdapter(db=db)
    auth_handler = StravaHandler(db=db, adapter=adapter)
    return TrainSessionHandler(
        db=db,
        adapter=adapter,
        auth_handler=auth_handler
    )

# 스케줄 새로 로드
@router.get("/fetch-new-schedules")
async def fetch_schedule(
    date:int,
    payload: TokenPayload = Depends(get_current_user),
    handler:TrainSessionHandler=Depends(get_handler)):
    
    return await handler.fetch_new_schedules(payload=payload, start_date=date)

# 스케줄 불러오기
@router.get("/fetch-schedules")
async def fetch_schedule(
    date:int,
    payload: TokenPayload = Depends(get_current_user),
    handler:TrainSessionHandler=Depends(get_handler)):
    
    return await handler.get_schedules(payload=payload, start_date=date)


# 스케줄 세부 정보
