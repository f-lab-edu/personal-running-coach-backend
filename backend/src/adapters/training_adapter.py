from typing import List, Tuple
import asyncio
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from ports.training_port import TrainingPort
from schemas.models import (ActivityData, 
                            LapData, 
                            StreamData, 
                            TrainResponse, TrainRequest,
                            TrainDetailResponse)
from infra.db.storage import activity_repo as repo
from config.exceptions import InternalError, CustomError

class TrainingAdapter(TrainingPort):
    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def save_session(self, user_id:UUID, 
                     activity:ActivityData,
                     laps:List[LapData],
                     stream:StreamData
                     )->bool:
        """훈련 세션  (TrainSession , Stream, Lap) 저장 
            같은 훈련은 스킵
        """
        try:
            session = await repo.add_train_session(db=self.db,
                                   user_id=user_id,
                                activity=activity)
            
            # 이미 db에 저장된 세션.
            if session is None:
                return False
            await asyncio.gather(
                repo.add_train_session_stream(db=self.db,session_id=session.id,stream=stream),
                repo.add_train_session_lap(db=self.db,session_id=session.id,laps=laps)
            )
            
            return True
            
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error save_session", original_exception=e)
        
        
    async def upload_session(self, user_id:UUID, 
                     session:TrainRequest = None,
                     laps:List[LapData] = None,
                     stream:StreamData = None)->bool:
        """훈련 세션  (TrainSession , Stream, Lap) 업로드. """
        try:

            activity = ActivityData(
                provider="local",
                activity_title=session.activity_title,
                analysis_result=session.analysis_result,
                elapsed_time=session.total_time,
                start_date=session.train_date,
                average_speed=session.avg_speed,
                distance=session.distance,   
            )
            res = await repo.add_train_session(db=self.db,
                                   user_id=user_id,
                                   activity=activity
                                   )
            if res:
                return True
            return False

        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error update_session", original_exception=e)
           
        
    def get_session_by_id(self, user_id:UUID, session_id:UUID, sport_type:str)->TrainResponse:
        """훈련 세션 받기"""
        ...
        
    async def get_session_detail(self, user_id:UUID, session_id:UUID)->TrainDetailResponse:
        """훈련 세션 세부 정보 받기 (stream, Lap)"""
        try:
            laps_orm, stream_orm = await asyncio.gather(
                repo.get_train_session_laps(user_id=user_id, session_id=session_id, db=self.db),
                repo.get_train_session_stream(user_id=user_id, session_id=session_id, db=self.db)
            )

            laps = [LapData.model_validate(lap) for lap in laps_orm]
            stream = StreamData.model_validate(stream_orm) if stream_orm else None

            return TrainDetailResponse(
                laps=laps,
                stream=stream
            )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_session_detail", original_exception=e)
        
    async def get_sessions_by_date(self, user_id:UUID, start_date:int = None)-> List[TrainResponse]:
        """기간 내의 훈련 세션 받기"""
        try:
            if start_date is not None:
                start_date = datetime.fromtimestamp(start_date, tz=timezone.utc).replace(tzinfo=None)
            else:
                cur = datetime.now(timezone.utc).replace(tzinfo=None)
                start_date = cur - timedelta(days=14)
                
            sessions = await repo.get_train_session_by_date(db=self.db,
                                        user_id=user_id,
                                        start_date=start_date)
            return [
                TrainResponse(
                    session_id=session.id,
                    train_date=session.train_date,
                    distance=session.distance,
                    avg_speed=session.avg_speed,
                    total_time=session.total_time,
                    activity_title=session.activity_title,
                    analysis_result=session.analysis_result
                ) for session in sessions
            ]
        
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_sessions_by_date", original_exception=e)

        
        
        
        
    def delete_session(self, user_id:UUID, session_id:int)->bool:
        """세션 삭제"""
        ...
    
    
    # ### 훈련 목표
    # def set_training_goal(self, user_id:UUID, training_goal:TrainGoal)->bool:
    #     ...
        
    # def update_training_goal(self, user_id:UUID, training_goal:TrainGoal)->bool:
    #     ...
        
    # def get_training_goal(self, user_id:UUID)->TrainGoal:
    #     ...
        
        