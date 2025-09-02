from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from adapters import StravaAdapter
from infra.db.storage.session import get_session
from infra.db.storage.third_party_token_repo import get_third_party_token_by_provider_user_id as get_strava_token
from use_cases.train_session.handle_train_session import TrainSessionHandler
from schemas.models import TokenPayload
from use_cases.auth.dependencies import get_current_user

router = APIRouter(prefix="/trainsession", tags=['train-session'])


def get_handler(db:AsyncSession=Depends(get_session))->TrainSessionHandler:
    return TrainSessionHandler(
        db=db,
        adapter=StravaAdapter(db=db)
    )


@router.get("/fetch-schedules")
async def fetch_schedule(
    payload: TokenPayload = Depends(get_current_user),
    handler:TrainSessionHandler=Depends(get_handler)):
    
    
    return await handler.update_schedules(payload=payload)
