"""훈련 데이터 db 핸들링 포트"""
from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from schemas.models import (ActivityData, 
                            LapData, 
                            StreamData, 
                            TrainResponse, TrainRequest,
                            TrainDetailResponse)

class TrainingPort(ABC):
    @abstractmethod
    async def save_session(self, user_id:UUID, 
                     activity:ActivityData,
                     laps:List[LapData],
                     stream:StreamData
                     )->bool:
        """훈련 세션  (TrainSession , Stream, Lap) 저장 """
        ...
        

    @abstractmethod
    async def upload_session(self, user_id:UUID, 
                     session:TrainRequest = None,
                     laps:List[LapData] = None,
                     stream:StreamData = None)->bool:
        """훈련 세션  (TrainSession , Stream, Lap) 업데이트. 수정된 부분만. """

        ...
        
    @abstractmethod
    async def get_session_by_id(self, user_id:UUID, session_id:UUID, sport_type:str)->TrainResponse:
        """훈련 세션 받기"""
        ...
        
    @abstractmethod
    async def get_session_detail(self, user_id:UUID, session_id:UUID)->TrainDetailResponse:
        """훈련 세션 세부 정보 받기 (stream, Lap)"""
        ...
        
    @abstractmethod
    async def get_sessions_by_date(self, user_id:UUID, start_date:int)-> List[TrainResponse]:
        """기간 내의 훈련 세션 받기"""
        ...
        
    @abstractmethod
    def delete_session(self, user_id:UUID, session_id:int)->bool:
        """세션 삭제"""
        ...
    
    
    # ### 훈련 목표
    # @abstractmethod
    # def set_training_goal(self, user_id:UUID, training_goal:TrainGoal)->bool:
    #     ...
        
    # @abstractmethod
    # def update_training_goal(self, user_id:UUID, training_goal:TrainGoal)->bool:
    #     ...
        
    # @abstractmethod
    # def get_training_goal(self, user_id:UUID)->TrainGoal:
    #     ...
        
        