from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from typing import Optional

from ports.llm_port import LLMPort
from ports.training_port import TrainingPort
from ports.account_port import AccountPort
from ports.llm_data_port import LLMDataPort
from schemas.models import TokenPayload, LLMResponse
from config.exceptions import CustomError, InternalError



class LLMHandler:
    def __init__(self, db:AsyncSession,
                 account_adapter:AccountPort,
                 training_adapter:TrainingPort,
                 llm_adapter:LLMPort,
                 llm_data_adapter:LLMDataPort
                 ):
        self.account_adapter = account_adapter
        self.llm_adapter = llm_adapter
        self.training_adapter = training_adapter
        self.llm_data_adapter = llm_data_adapter


    async def generate_trainings(self, payload:TokenPayload)->dict:
        try:
            user_info, sessions = await asyncio.gather(
                self.account_adapter.get_user_info_by_id(user_id=payload.user_id),
                self.training_adapter.get_sessions_by_date(user_id=payload.user_id)
            )
            res = await self.llm_adapter.generate_training_plan(user_info=user_info,
                                                            training_sessions=sessions)


            return res
    
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error generate_trainings", original_exception=e)

    async def generate_advices(self, payload:TokenPayload)->str:
        try:
            user_info, sessions = await asyncio.gather(
                self.account_adapter.get_user_info_by_id(user_id=payload.user_id),
                self.training_adapter.get_sessions_by_date(user_id=payload.user_id)
            )

            res = await self.llm_adapter.generate_coach_advice(user_info=user_info,
                                                            training_sessions=sessions)

            return res
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error generate_advices", original_exception=e)

    async def generate_trainings_advices(self, payload:TokenPayload, )->Optional[LLMResponse]:
        """llm 예측. 만약 리밋 기일 내에 실행됐으면 none 반환"""

        try:
            user_info, sessions, is_available = await asyncio.gather(
                self.account_adapter.get_user_info_by_id(user_id=payload.user_id),
                self.training_adapter.get_sessions_by_date(user_id=payload.user_id),
                # if exist, check period
                self.llm_data_adapter.is_llm_call_available(user_id=payload.user_id)

            )

            if not is_available:
                return None
            
            advice, plans = await asyncio.gather(
                self.llm_adapter.generate_coach_advice(user_info=user_info,training_sessions=sessions),
                self.llm_adapter.generate_training_plan(user_info=user_info,training_sessions=sessions)
            )
            
            # 데이터 저장
            response = await self.llm_data_adapter.save_llm_result(advice=advice, llm_sessions=plans, user_id=payload.user_id)
            return response

        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error generate_trainings_advices", original_exception=e)
    

    async def get_trainings_advices(self, payload:TokenPayload)->Optional[LLMResponse]:
        """db에 저장된 llm 예측 결과 받기"""
        try:
            return await self.llm_data_adapter.get_llm_predict(user_id=payload.user_id)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_trainings_advices", original_exception=e)