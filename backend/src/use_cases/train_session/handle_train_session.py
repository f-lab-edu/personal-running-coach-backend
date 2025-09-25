"""
training data 관련 유스케이스
"""
from typing import List
from uuid import UUID

from adapters.training_data_adapter import TrainingDataPort
from adapters.training_adapter import TrainingPort
from config.logger import get_logger
from schemas.models import TokenPayload, TrainResponse, LapData, StreamData, TrainDetailResponse
from use_cases.auth.auth_strava import StravaHandler
from domains.data_analyzer import DataAnalyzer
from config.exceptions import (DBError, TokenError,
                               AdapterError, 
                               InternalError, 
                               UsecaseError, 
                               UsecaseNotFoundError, 
                               UsecaseValidationError)

logger = get_logger(__file__)


class TrainSessionHandler:
    def __init__(self, data_adapter: TrainingDataPort,
                 db_adapter: TrainingPort,
                 auth_handler: StravaHandler,
                 ):
        self.data_adapter = data_adapter
        self.db_adapter = db_adapter
        self.auth_handler = auth_handler
        self.analyzer = DataAnalyzer()
        
    
    ## 스트라바 액세스 토큰 불러오기
    async def _get_access_token(self, payload:TokenPayload):
        return await self.auth_handler.get_access_and_refresh_if_expired(payload=payload)
        
        
    async def fetch_new_schedules(self, payload:TokenPayload, start_date:int = None) -> bool:
        """주어진 기간 이후의 활동들을 받아서 db에 저장.
                    1. 주어진 날 이후의 데이터 받기
                    2. db에 데이터 저장. db에 겹치는 활동은 저장안함
                    3. 리턴
        """
        try:
            
            ## 액세스 토큰
            access_token = await self._get_access_token(payload)
        
            if not access_token:
                raise UsecaseValidationError(message="invalid token")
            
            
            # 액티비티 리스트 
            activity_list = await self.data_adapter.fetch_activities(access_token=access_token,
                                                          after_date=start_date)

            # 각 액티비티
            # schedules = []
            for activity in activity_list:
                
                lap_data = await self.data_adapter.fetch_activity_lap(access_token=access_token,
                                                         activity_id=activity.activity_id)
                
                stream_data = await self.data_adapter.fetch_activity_stream(access_token=access_token,
                                                         activity_id=activity.activity_id)
                
                
                train_res = self.analyzer.analyze(activity=activity,
                                                            laps=lap_data,
                                                            stream=stream_data)
                activity.activity_title = train_res.get("title", "러닝")
                activity.analysis_result = train_res.get("detail", "세부내용 없음")  
                
                ## db 저장
                await self.db_adapter.save_session(user_id=payload.user_id,
                                             activity=activity,
                                             laps=lap_data,
                                             stream=stream_data
                                             )
            ## 사용자에게 리턴
            return True
                
        
        except (DBError, TokenError, AdapterError, UsecaseError, InternalError):
            raise
        except Exception as e:
            logger.exception(f"error fetch_new_schedules {e}")
            raise InternalError(exception=e)

    
    async def get_schedules(self, payload:TokenPayload, start_date:int = None) -> List[TrainResponse]:
        """db 에서 스케줄 받기"""
        try:
            
            return await self.db_adapter.get_sessions_by_date(user_id=payload.user_id,
                                                start_date=start_date)

        except (DBError, TokenError, AdapterError, UsecaseError, InternalError):
            raise
        except Exception as e:
            logger.exception(f"error get_schedules {e}")
            raise InternalError(exception=e)

    async def get_schedule_detail(self, payload:TokenPayload, session_id:UUID = None)->TrainDetailResponse:
        """db 에서 스케줄 세부정보 받기"""
        try:
            
            return await self.db_adapter.get_session_detail(user_id=payload.user_id,
                                                session_id=session_id)

        except (DBError, TokenError, AdapterError, UsecaseError, InternalError):
            raise
        except Exception as e:
            logger.exception(f"error get_schedules {e}")
            raise InternalError(exception=e)
        
    
    def upload_new_schedule(self, payload:TokenPayload, session:TrainResponse)->bool:
        """db에 사용자가 직접 입력한 훈련 저장 train_session 만"""
        ...
        
    def update_schedule(self, payload: TokenPayload, 
                        session: TrainResponse,
                        Laps:List[LapData],
                        ):
        """사용자가 수정한 훈련 업데이트. trainsession, lap"""
        ...