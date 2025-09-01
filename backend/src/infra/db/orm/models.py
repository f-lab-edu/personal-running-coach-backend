from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship

# --- User ---
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str
    hashed_pwd: Optional[str] = Field(default=None) 
    name: Optional[str] = Field(default=None)  # Make name optional for OAuth users
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = Field(default="local")  # Default to "local" for email/password users

    tokens: List["Token"] = Relationship(back_populates="user")
    third_party_tokens: List["ThirdPartyToken"] = Relationship(back_populates="user")
    train_sessions: List["TrainSession"] = Relationship(back_populates="user")
    llms: List["LLM"] = Relationship(back_populates="user")

class Token(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    refresh_token: str
    expires_at: int
    
    user: Optional[User] = Relationship(back_populates="tokens")


class ThirdPartyToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    provider: str  # 'strava', 'google', 'naver' 등
    provider_user_id:str # 외부 서비스 아이디
    access_token: str
    refresh_token: str
    expires_at: int  # UNIX timestamp 혹은 datetime으로 변경 가능
    extra_data: Optional[str] = None  

    user: Optional["User"] = Relationship(back_populates="third_party_tokens")
    
    

class TrainSession(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    activity_id: Optional[int] = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    train_date: datetime
    train_type: str
    train_detail: str = Field(default="") ## ex) 훈련 간략 설명


    user: Optional[User] = Relationship(back_populates="train_sessions")
    result: Optional["TrainSessionResult"] = Relationship(back_populates="session")
    

class TrainSessionResult(SQLModel, table=True):
    """heartrate,watts,cadence,distance,velocity_smooth,altitude"""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: Optional[UUID] = Field(foreign_key="trainsession.id", nullable=False)
    stream_heartrate: Optional[str] = None  # json/text
    stream_watts: Optional[str] = None  # json/text
    stream_cadence: Optional[str] = None  # json/text
    stream_distance: Optional[str] = None  # json/text
    stream_velocity: Optional[str] = None  # json/text
    stream_altitude: Optional[str] = None  # json/text
    analysis_result: Optional[str] = None
    
    session: Optional[TrainSession] = Relationship(back_populates="result")
    
class LLM(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    llm_type: str     #TODO: enum
    llm_result: str

    user: Optional[User] = Relationship(back_populates="llms")
