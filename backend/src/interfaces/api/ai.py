from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.models import TokenPayload
from infra.db.storage.session import get_session
from adapters import LLMAdapter, TrainingAdapter, AccountAdapter, LLMDataAdapter
from use_cases.training_llm import LLMHandler
from use_cases.auth.dependencies import get_current_user, get_test_user
from config.settings import llm
from config.exceptions import CustomError
from config.logger import get_logger

logger = get_logger(__name__)




router = APIRouter(prefix="/ai", tags=["ai"])

def get_handler(db:AsyncSession=Depends(get_session))->LLMHandler:
        return LLMHandler(
            db=db,
            account_adapter=AccountAdapter(db=db),
            llm_adapter=LLMAdapter(llm.secret),
            training_adapter=TrainingAdapter(db=db),
            llm_data_adapter=LLMDataAdapter(db=db)
        )
    


@router.post("/session")
async def llm_prediction(
    payload: TokenPayload = Depends(get_current_user),
    handler:LLMHandler = Depends(get_handler)
):
    # 사용자 데이터 기반 훈련 생성
    try:
        return await handler.generate_trainings(payload=payload)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"llm_prediction. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/coach-advice")
async def coach_advice(
    payload: TokenPayload = Depends(get_current_user),
    handler:LLMHandler = Depends(get_handler)
):
    try:
        return await handler.generate_advices(payload=payload)
    # 사용자 데이터 기반 코치 조언 생성
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"coach_advice. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/generate")
async def generate(
    payload: TokenPayload = Depends(get_current_user),
    handler:LLMHandler = Depends(get_handler)
):
    try:
        return await handler.generate_trainings_advices(payload=payload)
    # 사용자 데이터 기반 코치 조언 생성
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"generate. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.get("/get")
async def get_llm(
    payload: TokenPayload = Depends(get_current_user),
    handler:LLMHandler = Depends(get_handler)
):
    try:
        return await handler.get_trainings_advices(payload=payload)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"get_llm. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    