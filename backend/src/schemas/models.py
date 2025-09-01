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
    

############### 응답모델
class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class AccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None 
    provider: str = "local"
    
class LoginResponse(BaseModel):
    token: Optional[TokenResponse] = None
    user: AccountResponse
    connected: List[str] = []
    


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
    
########

class TrainStreamResponse(BaseModel):
    heartrate: Optional[List[float]] = None
    cadence: Optional[List[float]] = None
    distance: Optional[List[float]] = None
    velocity: Optional[List[float]] = None
    altitude: Optional[List[float]] = None

class TrainResponse(BaseModel):
    session_id:UUID
    created_at:datetime
    train_date:datetime
    train_type:str
    train_detail:str
    distance:Optional[float] = None
    avg_speed: Optional[float] = None
    total_time: Optional[float] = None
    streams: Optional[TrainStreamResponse] = None
    analysis_result: Optional[str] = None
    
    
    
class TrainGoal(BaseModel):
    user_id:UUID
    goal:str
    target_date:datetime
    created_at:datetime
    
class CoachAdvice(BaseModel):
    user_id:UUID
    created_at:datetime
    advice:str
    
    