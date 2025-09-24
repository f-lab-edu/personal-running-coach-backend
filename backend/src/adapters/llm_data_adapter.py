"""llm 결과 저장 db 데이터 """

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from schemas.models import LLMResponse
from ports.llm_data_port import LLMDataPort
from infra.db.orm.models import LLM
from infra.db.storage import llm_repo as repo
from config.logger import get_logger
from config.exceptions import AdapterNotFoundError, AdapterError, AdapterValidationError, InternalError, DBError

logger = get_logger(__file__)

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
        except DBError:
            raise
        except Exception as e:
            logger.exception(f"error save_llm_result {e}")
            raise InternalError(exception=e)

    async def get_llm_predict(self, user_id:UUID, )->Optional[LLMResponse] :
        try:
            saved = await repo.get_llm_predict_by_user_id(db=self.db, user_id=user_id)

            if saved:
                return LLMResponse(
                    sessions=saved.workout,
                    advice=saved.coach_advice
                )
            return None
        except DBError:
            raise
        except Exception as e:
            logger.exception(f"error get_llm_predict {e}")
            raise InternalError(exception=e)

    
    async def is_llm_call_available(self, user_id:UUID, limiter_day:int=7) -> bool:
        try:
            saved = await repo.get_llm_predict_by_user_id(db=self.db, user_id=user_id)

            if not saved: 
                return True
            
            # 정해진 기일 내 한번 리밋
            next_available = saved.executed_at + timedelta(days=limiter_day)
            print(f"{next_available} < {datetime.now(timezone.utc)} ???")
            return datetime.now(timezone.utc).replace(tzinfo=None) >= next_available
        except DBError:
            raise
        except Exception as e:
            logger.exception(f"error is_llm_call_available {e}")
            raise InternalError(exception=e)