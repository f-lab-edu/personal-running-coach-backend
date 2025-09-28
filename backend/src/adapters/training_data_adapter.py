from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import httpx
import numpy as np
from datetime import datetime, timezone, timedelta


from ports.training_data_port import TrainingDataPort
from typing import Optional, List
from config.settings import strava
from infra.db.storage import third_party_token_repo as repo
from infra.db.orm.models import ThirdPartyToken
from schemas.models import LapData, StreamData, ActivityData
from config.exceptions import InternalError, DBError, CustomError


class StravaAdapter(TrainingDataPort):
    def __init__(self, db:AsyncSession):
        self.db = db
    
    async def connect(self, auth_code: str) -> dict:
        """플랫폼에 연결. 스트라바 토큰 받기"""
        try:
            payload = {
                "client_id": strava.client_id,
                "client_secret": strava.client_secret,
                "code": auth_code,
                "grant_type": "authorization_code"
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(strava.token_url, data=payload)
            
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise InternalError(context="Strava httpx call error", original_exception=e)
        except Exception as e:
            raise InternalError(context="error strava connect", original_exception=e)
        
    
    async def disconnect(self, user_id: UUID) -> bool:
        """플랫폼 연결 해제"""
        # 1. DB에서 액세스 토큰 가져오기
        try:
            access_token = await repo.get_third_party_token_by_user_id(
                db=self.db,
                provider="strava",
                user_id=user_id
            )
            
            if not access_token:
                return True  # 이미 끊겨 있음
            
            
            headers = {"Authorization": f"Bearer {access_token}"}
            url = strava.deauth_endpoint
            
            # strava 에서 연결 끊기        
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(url, headers=headers)
                except httpx.HTTPError:
                    pass
                
            # db 에서 토큰 삭제
            await repo.delete_third_party_token(
                db=self.db,
                provider="strava",
                user_id=user_id
            )
            
            return True
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error strava disconnect", original_exception=e)
        
    
    async def get_token_from_db(self, user_id:UUID)->Optional[ThirdPartyToken]:
        """get 서드파티토큰
            access, refresh, expires_at, ...
        """
        try:
            return await repo.get_third_party_token_by_user_id(
                                db=self.db,
                                provider="strava",
                                user_id=user_id
                            )
        except DBError:
            raise
        except Exception as e:
            raise InternalError(context="error get_token_from_db", original_exception=e)
        
    
    async def fetch_activities(self, access_token:str, after_date: int = None) -> List[ActivityData]:
        """훈련 활동 데이터 가져오기
            user_id = 사용자 분류
            after_date = 시작날짜 (timestamp)
            
            return : ActivityData 리스트
        """
        # get 액세스 토큰

        # 헤더 
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            url = strava.api_url + "athlete/activities"
            
            # 시작날짜 파라미터로
            if after_date is None:
                two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
                after_date = int(two_weeks_ago.timestamp())
                
            params = {
                "after": after_date,
                "per_page": 100   # 최대 200까지 가능
            }
            
            # activities
            async with httpx.AsyncClient() as client:
                response = await client.get(url=url, headers=headers, params=params)
                response.raise_for_status()
                
                return self._parse_activity_data(response.json())
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise InternalError(context=f"Strava httpx call error", original_exception=e)
        except Exception as e:
            raise InternalError(context="error fetch_activities", original_exception=e)
        
    def _parse_activity_data(self, res:list) -> List[ActivityData]:
        """액티비티 데이터 포맷 - list > dic """
        ActivityData_list = [
            ActivityData(
                activity_id = activity['id'],
                provider="strava",
                distance = activity['distance'],
                elapsed_time = activity['elapsed_time'],
                sport_type = activity['sport_type'],
                start_date = activity['start_date_local'],
                average_speed = activity['average_speed'],
                max_speed = activity['max_speed'],
                average_heartrate = activity['average_heartrate'],
                max_heartrate = activity['max_heartrate'],
                average_cadence=activity['average_cadence'] *2
                ) for activity in res
        ]
        
            
        return ActivityData_list
        
    
    async def fetch_activity_stream(self, access_token:str, activity_id:int) -> StreamData:

        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            params = {
                "keys": "heartrate,watts,cadence,distance,velocity_smooth,time, altitude",
                "key_by_type": "true"
            }
            
            url = strava.api_url + f"activities/{activity_id}/streams"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                # 데이터 파이단틱 모델로 파싱
                return self._parse_stream_data(response.json())
            
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise InternalError(context=f"Strava httpx call error", original_exception=e)
        except Exception as e:
            raise InternalError(context="error fetch_activity_stream", original_exception=e)
        
            
        
    def _parse_stream_data(self, res:dict) -> StreamData:
        """스트림 데이터 포맷 - dictionary 
            {
                watts, cadence, velocity_smooth, time, heartrate, distance, altitude : {
                    data:[],
                    series_type:"distance",
                    original_size:int,
                    resolution:"high"
                }
            }
        """
        
        return StreamData(
                heartrate=res.get('heartrate',{}).get('data'),
                cadence=(np.array(res.get('cadence',{}).get('data')) * 2).tolist(),
                distance=res.get('distance',{}).get('data'), 
                velocity=res.get('velocity_smooth', {}).get('data'),
                altitude=res.get("altitude", {}).get('data'),
                time=res.get('time',{}).get('data'),
            )

        
            
    async def fetch_activity_lap(self, access_token:str, activity_id:int) -> List[LapData]:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            url = strava.api_url + f"activities/{activity_id}/laps"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                # 데이터 파싱
                parsed = self._parse_lap_data(response.json())
                
                return parsed
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise InternalError(context=f"Strava httpx call error", original_exception=e)
        except Exception as e:
            raise InternalError(context="error fetch_activity_lap", original_exception=e)
        
    
    def _parse_lap_data(self, res)->List[LapData]:
        """랩데이터 포맷 - [ 각 랩별 dic format]
            [
                {id, resource_state, elapsed_time, distance, average_speed,
                max_speed, lap_index, averge_cadence, average_heartrate, 
                max_heartrate, total_elevation_gain, pace_zone, ...
                },
                ...
            ]
        """
        laps = []
        for lap in res:
            laps.append(
                LapData(
                    lap_index=lap['lap_index'],
                    distance = lap['distance'],
                    elapsed_time=lap['elapsed_time'],
                    average_speed = lap['average_speed'],
                    max_speed = lap['max_speed'],
                    average_heartrate= lap['average_heartrate'],
                    max_heartrate= lap['max_heartrate'],
                    average_cadence= lap['average_cadence'] * 2,
                    elevation_gain= lap['total_elevation_gain'],
                )
            )
            
        return laps
        
        
        
    async def is_token_expired(self, expires_at:int) -> bool:
        """토큰 만료 검증"""
        now = int(datetime.now(timezone.utc).timestamp())
        print(f"now: {now} vs expires {expires_at}")
        return expires_at <= now

    
    async def refresh_token(self, refresh_token: str) -> dict:
        """토큰 갱신. db 업데이트"""
        try:
            payload = {
                "client_id": strava.client_id,
                "client_secret": strava.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url=strava.token_url, data=payload)
            
            response.raise_for_status()
            return response.json()
    
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            raise InternalError(context=f"Strava httpx call error", original_exception=e)
        except Exception as e:
            raise InternalError(context="error strava refresh_token", original_exception=e)
        
