from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.models import TokenPayload
from infra.db.storage.session import get_session
from adapters import LLMAdapter, TrainingAdapter, AccountAdapter
from use_cases.training_llm import LLMHandler
from use_cases.auth.dependencies import get_current_user, get_test_user

router = APIRouter(prefix="/ai", tags=["ai"])

from config.settings import llm

def get_handler(db:AsyncSession=Depends(get_session))->LLMHandler:
    
    return LLMHandler(
        db=db,
        account_adapter=AccountAdapter(db=db),
        llm_adapter=LLMAdapter(llm.secret),
        training_adapter=TrainingAdapter(db=db)
    )


@router.get("/session-predict")
async def llm_prediction(
    payload: TokenPayload = Depends(get_test_user),
    handler:LLMHandler = Depends(get_handler)
):
    # 사용자 데이터 기반 훈련 생성
    return await handler.generate_trainings(payload=payload)
    
@router.post("/coach-advice")
async def coach_advice(
    payload: TokenPayload = Depends(get_test_user),
    handler:LLMHandler = Depends(get_handler)
):
    # 사용자 데이터 기반 코치 조언 생성
    ...