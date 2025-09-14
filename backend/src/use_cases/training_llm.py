from sqlalchemy.ext.asyncio import AsyncSession

from ports.llm_port import LLMPort
from ports.training_port import TrainingPort
from ports.account_port import AccountPort
from schemas.models import TokenPayload
from config.logger import get_logger

logger = get_logger(__file__)

class LLMHandler:
    def __init__(self, db:AsyncSession,
                 account_adapter:AccountPort,
                 training_adapter:TrainingPort,
                 llm_adapter:LLMPort,
                 ):
        self.account_adapter = account_adapter
        self.llm_adapter = llm_adapter
        self.training_adapter = training_adapter


    async def generate_trainings(self, payload:TokenPayload)->dict:
        
        user_info = await self.account_adapter.get_user_info_by_id(user_id=payload.user_id)
        sessions = await self.training_adapter.get_sessions_by_date(user_id=payload.user_id)
        res = await self.llm_adapter.generate_training_plan(user_info=user_info,
                                                        training_sessions=sessions)


        return res

    async def generate_advices(self, payload:TokenPayload)->str:

        user_info = self.account_adapter.get_user_info_by_id(user_id=payload.user_id)

        sessions = self.training_adapter.get_sessions_by_date(user_id=payload.user_id)

        res = await self.llm_adapter.generate_coach_advice(user_info=user_info,
                                                        training_sessions=sessions)


        return res