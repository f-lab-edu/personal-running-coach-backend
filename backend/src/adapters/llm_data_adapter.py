"""llm 결과 저장 db 데이터 """

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from schemas.models import LLMResponse
from ports.llm_data_port import LLMDataPort
from infra.db.orm.models import LLM
from infra.db.storage import llm_repo as repo
from config.exceptions import InternalError, CustomError


class LLMDataAdapter(LLMDataPort):
    def __init__(self, db:AsyncSession):
        self.db = db

    async def save_llm_result(self, user_id:UUID, 
                              llm_sessions:List[dict], 
                              advice:Optional[str])->LLMResponse :
        try:
            llm = await repo.get_llm_predict_by_user_id(db=self.db, user_id=user_id)

            if llm:
                llm.workout = llm_sessions
                llm.coach_advice = advice
            else:
                llm = LLM(
                    user_id=user_id,
                    workout=llm_sessions,
                    coach_advice=advice
                )

            saved = await repo.save_llm_predict(db=self.db,llm=llm)
            
            return LLMResponse(
                sessions=saved.workout,
                advice=saved.coach_advice
            )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error save_llm_result", original_exception=e)

    async def get_llm_predict(self, user_id:UUID, )->Optional[LLMResponse] :
        try:
            saved = await repo.get_llm_predict_by_user_id(db=self.db, user_id=user_id)

            if saved:
                return LLMResponse(
                    sessions=saved.workout,
                    advice=saved.coach_advice
                )
            return None
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_llm_predict", original_exception=e)

    
    async def is_llm_call_available(self, user_id:UUID, limiter_day:int=7) -> bool:
        try:
            saved = await repo.get_llm_predict_by_user_id(db=self.db, user_id=user_id)

            if not saved: 
                return True
            
            # 정해진 기일 내 한번 리밋
            next_available = saved.executed_at + timedelta(days=limiter_day)
            return datetime.now(timezone.utc).replace(tzinfo=None) >= next_available
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error is_llm_call_available", original_exception=e)