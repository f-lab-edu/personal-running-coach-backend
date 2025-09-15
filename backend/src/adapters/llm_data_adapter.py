"""llm 결과 저장 db 데이터 """

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from schemas.models import LLMResponse, dict
from ports.llm_data_port import LLMDataPort
from infra.db.orm.models import LLM
from infra.db.storage import llm_repo as repo

class LLMDataAdapter(LLMDataPort):
    def __init__(self, db:AsyncSession):
        self.db = db

    async def save_llm_result(self, user_id:UUID, 
                              llm_sessions:List[dict], 
                              advice:Optional[str])->LLMResponse :
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

    async def get_llm_predict(self, user_id:UUID, )->Optional[LLMResponse] :
        return await repo.get_llm_predict_by_user_id(db=self.db, user_id=user_id)

        
