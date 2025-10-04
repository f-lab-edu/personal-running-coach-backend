"""
training data 관련 유스케이스
"""
from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone

from adapters.training_data_adapter import TrainingDataPort
from adapters.training_adapter import TrainingPort
from adapters.redis_adapter import RedisPort
from schemas.models import (TokenPayload, 
                            TrainResponse, 
                            TrainRequest, 
                            LapData, 
                            TrainDetailResponse,
                            TrainSessionResponse
                            )
from use_cases.auth.auth_strava import StravaHandler
from domains.data_analyzer import DataAnalyzer
from config.exceptions import (CustomError, InternalError, NotModifiedError, ValidationError)
from infra.etag import generate_etag, serialize_train_response
from config.constants import ETAG_TRAIN_SESSION


class TrainSessionHandler:
    def __init__(self, data_adapter: TrainingDataPort,
                 db_adapter: TrainingPort,
                 redis_adapter: RedisPort,
                 auth_handler: StravaHandler,
                 ):
        self.data_adapter = data_adapter
        self.db_adapter = db_adapter
        self.redis_adapter = redis_adapter
        self.auth_handler = auth_handler
        self.analyzer = DataAnalyzer()
        self.etagpage = ETAG_TRAIN_SESSION
        
    
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
                raise ValidationError(detail="invalid token")
            
            
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
                
            # 데이터 수정 시점 : etag 만료 
            await self.redis_adapter.remove_user_etag(user_id=payload.user_id,
                                                page=ETAG_TRAIN_SESSION)

            ## 사용자에게 리턴
            return True
                
        
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error fetch_new_schedules", original_exception=e)

    
    async def get_schedules(self, payload:TokenPayload, etag:str = None, start_date:int = None) -> TrainSessionResponse:
        """db 에서 스케줄 받기
            etag 받아서 확인. 변경사항 없을시 304 NotModified 에러 출력.
            사용자 etag 와 데이터 etag 가 매치하지 않을 경우 데이터 내보내기 
        """
        # {"etag": str, "data": List[TrainResponse]}
        try:
            redis_etag = await self.redis_adapter.get_user_etag(user_id=payload.user_id,page=ETAG_TRAIN_SESSION)
            
            # 사용자 etag 가 서버와 매칭할 경우 304 
            if redis_etag is not None and etag is not None and redis_etag == etag :
                raise NotModifiedError(context="data not modified")

            # etag 미스매치. etag 생성 및 데이터 + etag 반환
            data =  await self.db_adapter.get_sessions_by_date(user_id=payload.user_id,
                                                start_date=start_date)
            data_serializable = [serialize_train_response(item) for item in data]
            etag = await generate_etag(data_serializable)
            print(etag)
            await self.redis_adapter.set_user_etag(user_id=payload.user_id,
                                                page=ETAG_TRAIN_SESSION,
                                                etag= etag)

            return TrainSessionResponse(
                etag=etag,
                data=data
            )

        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_schedules", original_exception=e)

    async def get_schedule_detail(self, payload:TokenPayload, session_id:UUID = None)->TrainDetailResponse:
        """db 에서 스케줄 세부정보 받기"""
        try:
            
            return await self.db_adapter.get_session_detail(user_id=payload.user_id,
                                                session_id=session_id)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_schedule_detail", original_exception=e)

    
    async def upload_new_schedule(self, payload:TokenPayload, session:TrainRequest)->bool:
        """db에 사용자가 직접 입력한 훈련 저장 train_session 만"""
        try:
            res = await self.db_adapter.upload_session(user_id=payload.user_id,
                                                        session=session
                                                        )
        
            # redis etag 삭제 
            await self.redis_adapter.remove_user_etag(user_id=payload.user_id,
                                                page=ETAG_TRAIN_SESSION)
            return res

        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error upload_new_schedule", original_exception=e)

    



    def update_schedule(self, payload: TokenPayload, 
                        session: TrainResponse,
                        Laps:List[LapData],
                        ):
        """사용자가 수정한 훈련 업데이트. trainsession, lap"""
        ...