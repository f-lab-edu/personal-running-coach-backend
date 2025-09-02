"""
training data 관련 유스케이스
get activities
get each activity stream

"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import Optional, List
from uuid import UUID

from adapters.training_data_adapter import TrainingDataPort
from config.logger import get_logger
from infra.db.orm.models import TrainSessionResult, TrainSession
from schemas.models import TrainStreamResponse, TrainResponse, TokenPayload
from infra.db.storage import third_party_token_repo as repo 
from use_cases.auth.auth_strava import StravaHandler


logger = get_logger(__file__)


class TrainSessionHandler:
    def __init__(self, db: AsyncSession, adapter: TrainingDataPort):
        self.db = db
        self.adapter = adapter
        self.auth_handler = StravaHandler(db=db,adapter=adapter)
        
    
    
    async def _get_access_token(self, payload:TokenPayload):
        return await self.auth_handler.get_access_and_refresh_if_expired(payload=payload)
        
        
    async def update_schedules(self, payload:TokenPayload, after_date:int = None) -> List[TrainResponse]:
        """주어진 기간 이후의 활동들을 받아서 db에 저장.
                    1. 주어진 날 이후의 데이터 받기
                    2. db에 데이터 저장. db에 겹치는 활동은 저장안함
                    3. 리턴
        """
        try:
            ## 액세스 토큰
            access_token = await self._get_access_token(payload)
        
            if not access_token:
                raise HTTPException(status_code=400, detail="token returned None.")
            
            
            # 액티비티 리스트 
            # TODO: 이미 받은 데이터는 제외.
            activity_list = await self.adapter.get_activities(access_token=access_token,
                                                          after_date=after_date)
            
            # 각 액티비티
            for activity in activity_list:
                activity_id = activity['id']
                
                lap_data = await self.adapter.get_activity_lap(access_token=access_token,
                                                         activity_id=activity_id)
                stream_data = await self.adapter.get_activity_stream(access_token=access_token,
                                                         activity_id=activity_id)
                
                
        
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail="internal server error")
        
        
    def upload_schedule(self):
        ...