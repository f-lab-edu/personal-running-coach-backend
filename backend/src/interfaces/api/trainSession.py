from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from adapters import StravaAdapter
from infra.db.storage.session import get_session
from infra.db.storage.third_party_token_repo import get_third_party_token_by_provider_user_id as get_strava_token
from use_cases.train_session.handle_train_session import TrainSessionHandler
from schemas.models import TokenPayload

router = APIRouter(prefix="/trainsession", tags=['train-session'])


def get_handler(db:AsyncSession=Depends(get_session))->TrainSessionHandler:
    return TrainSessionHandler(
        db=db,
        adapter=StravaAdapter(db=db)
    )


@router.get("/fetch")
async def fetch_schedule(db:AsyncSession=Depends(get_session)):
    adapter = StravaAdapter(db=db)
    user_id = UUID("0ec20e98eb3c4ebf820131f41a4c7bb9")
    token = await adapter.get_token_from_db(user_id)
    
    expired = await adapter.is_token_expired(token.expires_at)
    print("expired: ",expired)
    # if expired:
    #     new_token = await adapter.refresh_token(token.refresh_token)
    #     print(new_token)
    #     return new_token
    # else:
    #     return token
    return token
@router.get("/refresh")
async def fetch_schedule(handler:TrainSessionHandler=Depends(get_handler)):
    
    user_id = UUID("0ec20e98eb3c4ebf820131f41a4c7bb9")
    payload = TokenPayload(
        user_id=user_id,
        exp=123,
        iat=1234,
        token_type="acess"
    )
    
    # 리프레시 토큰 테스트
    return await handler._get_access_token(payload)
    
    # token = await adapter.get_token_from_db(user_id)
    
    # handler.get_valid_token()
    
    # # expired = await adapter.is_token_expired(token.expires_at)
    # # print("expired: ",expired)
    # # if expired:
    # print("refresh:",repr(token.refresh_token))
    # new_token = await adapter.refresh_token(
    #                                 user_id=user_id,
    #                                 refresh_token=token.refresh_token)
    # print(new_token)
    # return new_token



# @router.put("/{session_id}", response_model=TrainSession)
# async def edit_schedule(session_id:str, session_data:TrainSession):
#     ...

# @router.post("/upload-training", response_model=TrainSession)
# async def upload_training(session_data:TrainSession):
#     ...
