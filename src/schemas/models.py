from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID



class TokenPayload(BaseModel):  ## jwt payload 용
    user_id:UUID
    exp:int
    iat:int
    token_type:str = 'access'  # or "refresh"
    

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

class TrainSession(BaseModel):
    session_id:str
    created_at:datetime
    distance:float
    stream_data:dict  ## TODO heartrate,watts,
    
    
class TrainGoal(BaseModel):
    user_id:UUID
    goal:str
    target_date:datetime
    created_at:datetime
    
class CoachAdvice(BaseModel):
    user_id:UUID
    created_at:datetime
    advice:str
    
    