from typing import List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from ports.training_port import TrainingPort
from schemas.models import ActivityData, LapData, StreamData, TrainResponse, TrainGoal
from infra.db.storage import activity_repo as repo


class TrainingAdapter(TrainingPort):
    def __init__(self, db:AsyncSession):
        self.db = db
    
    def save_session(self, user_id:UUID, 
                     session:ActivityData,
                     laps:List[LapData],
                     stream:StreamData
                     )->bool:
        """훈련 세션  (TrainSession , Stream, Lap) 저장 
            같은 훈련은 스킵
        """
        ...
        
    def update_session(self, user_id:UUID, 
                     session:ActivityData = None,
                     laps:List[LapData] = None,
                     stream:StreamData = None)->bool:
        """훈련 세션  (TrainSession , Stream, Lap) 업데이트. 수정된 부분만. """

        ...
        
    def get_session_by_id(self, user_id:UUID, session_id:int, sport_type:str)->TrainResponse:
        """훈련 세션 받기"""
        ...
        
    def get_session_detail(self, user_id:UUID, session_id:int)->Tuple[List[LapData], StreamData]:
        """훈련 세션 세부 정보 받기 (stream, Lap)"""
        ...
        
    def get_sessions_by_date(self, user_id:UUID, start_date:int)-> List[TrainResponse]:
        """기간 내의 훈련 세션 받기"""
        ...
        
    def delete_session(self, user_id:UUID, session_id:int)->bool:
        """세션 삭제"""
        ...
    
    
    ### 훈련 목표
    def set_training_goal(self, user_id:UUID, training_goal:TrainGoal)->bool:
        ...
        
    def update_training_goal(self, user_id:UUID, training_goal:TrainGoal)->bool:
        ...
        
    def get_training_goal(self, user_id:UUID)->TrainGoal:
        ...
        
        