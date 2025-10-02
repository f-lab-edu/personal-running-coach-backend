from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID



class TokenPayload(BaseModel):  ## jwt payload 용
    user_id:UUID
    exp:int
    iat:int
    token_type:str = 'access'  # or "refresh"
    
class RefreshTokenResult(BaseModel):
    token:str
    expires_at:int




    
########
# raw data -> 분석모델 
class LapData(BaseModel):
    lap_index: int
    distance: float  # meters
    elapsed_time: int  # seconds
    average_speed: float  # m/s
    max_speed: float  # m/s
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    average_cadence: Optional[float] = None
    elevation_gain:Optional[float] = None

    class Config:
        from_attributes = True  # ORM 객체 지원

class StreamData(BaseModel):
    heartrate: Optional[List[float]] = None
    cadence: Optional[List[float]] = None
    distance: Optional[List[float]] = None
    velocity: Optional[List[float]] = None
    altitude: Optional[List[float]] = None
    time: Optional[List[float]] = None

    class Config:
        from_attributes = True  # ORM 객체 지원

class ActivityData(BaseModel):
    activity_id: Optional[int] = None
    provider: Optional[str] = None
    distance: Optional[float] = None
    elapsed_time: int
    sport_type: Optional[str] = None
    start_date: datetime
    average_speed:Optional[float] = None
    max_speed:Optional[float] = None
    average_heartrate:Optional[float] = None
    max_heartrate:Optional[float] = None
    average_cadence:Optional[float] = None
    activity_title:Optional[str] = None
    analysis_result : Optional[str] = None

class UserInfoData(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    train_goal: Optional[str] = None

    class Config:
        from_attributes = True  # ORM 객체 지원
    
class LLMSessionResult(BaseModel):
    day: str
    workout_type: str
    distance_km: float
    pace: Optional[str] = None
    notes: Optional[str] = None





####### 요청 모델
# 일반 로그인
class LoginRequest(BaseModel):
    email: EmailStr
    pwd: str 

# 회원가입 요청
class SignupRequest(BaseModel):
    email: EmailStr
    pwd: str
    name: str

class AccountRequest(BaseModel):
    name:Optional[str] = None
    pwd:Optional[str] = None
    provider:Optional[str] = None
    info:Optional[UserInfoData] = None

# 세션 추가
class TrainRequest(BaseModel):
    train_date:datetime
    distance:Optional[float] = None
    avg_speed: Optional[float] = None
    total_time: Optional[float] = None
    activity_title:Optional[str] = None
    analysis_result: Optional[str] = None



############### 응답모델
class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class AccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    provider: str
    info: Optional[UserInfoData] = None
    

    
class LoginResponse(BaseModel):
    token: Optional[TokenResponse] = None
    user: AccountResponse
    device_id: Optional[UUID] = None
    connected: List[str] = []
    
class TrainResponse(BaseModel):
    session_id:UUID
    train_date:datetime
    distance:Optional[float] = None
    avg_speed: Optional[float] = None
    total_time: Optional[float] = None
    activity_title:Optional[str] = None
    analysis_result: Optional[str] = None

class TrainSessionResponse(BaseModel):
    etag:Optional[str] = None
    data:List[TrainResponse]

class TrainDetailResponse(BaseModel):
    laps:Optional[List[LapData]] = None
    stream : Optional[StreamData] = None

class LLMResponse(BaseModel):
    sessions:Optional[List[LLMSessionResult]] = None
    advice:Optional[str] = None