from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Column, JSON, UniqueConstraint
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
    provider: Optional[str] = None
    activity_id: int = Field(index=True)
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))
    train_date: datetime
    distance:Optional[float] = None
    avg_speed: Optional[float] = None
    total_time: Optional[float] = None
    analysis_result: Optional[str] = None
    
    user: Optional[User] = Relationship(back_populates="train_sessions")
    stream: Optional["TrainSessionStream"] = Relationship(back_populates="session")
    laps: List["TrainSessionLap"] = Relationship(back_populates="session")
    
    __table_args__ = (
        UniqueConstraint("provider", "activity_id", name="uq_provider_activity"),
    )
    

class TrainSessionStream(SQLModel, table=True):
    # 스트림 데이터는 jsonstring 으로 저장
    session_id: UUID = Field(foreign_key="trainsession.id", primary_key=True)
    heartrate: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
    cadence: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
    distance: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
    velocity: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
    altitude: Optional[List[float]] = Field(default=None, sa_column=Column(JSON))
    session: Optional[TrainSession] = Relationship(back_populates="stream")
    
class TrainSessionLap(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: Optional[UUID] = Field(foreign_key="trainsession.id", nullable=False)
    lap_index: int
    distance: float  # meters
    elapsed_time: int  # seconds
    average_speed: float  # m/s
    max_speed: float  # m/s
    average_heartrate: Optional[float] = None
    max_heartrate: Optional[float] = None
    average_cadence: Optional[float] = None
    elevation_gain:Optional[float] = None
    
    session: Optional[TrainSession] = Relationship(back_populates="laps")
    
class LLM(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
    llm_type: str     #TODO: enum
    llm_result: str

    user: Optional[User] = Relationship(back_populates="llms")
