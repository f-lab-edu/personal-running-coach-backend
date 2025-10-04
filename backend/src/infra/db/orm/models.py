from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Column, JSON, UniqueConstraint, DateTime
from sqlmodel import SQLModel, Field, Relationship

# --- User ---
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str
    hashed_pwd: Optional[str] = Field(default=None) 
    name: Optional[str] = Field(default=None)  # Make name optional for OAuth users
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    provider: str = Field(default="local")  # Default to "local" for email/password users

    user_info:List["UserInfo"] = Relationship(back_populates="user", cascade_delete=True)
    tokens: List["Token"] = Relationship(back_populates="user", cascade_delete=True)
    third_party_tokens: List["ThirdPartyToken"] = Relationship(back_populates="user", cascade_delete=True)
    train_sessions: List["TrainSession"] = Relationship(back_populates="user", cascade_delete=True)
    llms: List["LLM"] = Relationship(back_populates="user")

class UserInfo(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    height:Optional[float] = None
    weight:Optional[float] = None
    age:Optional[int] = None
    sex:Optional[str] = None
    train_goal: Optional[str] = None

    user: Optional[User] = Relationship(back_populates="user_info")

class Token(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    device_id: UUID = Field(default_factory=uuid4)
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
    activity_id: Optional[int] = None
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    train_date: datetime
    distance:Optional[float] = None
    avg_speed: Optional[float] = None
    total_time: Optional[float] = None
    activity_title: Optional[str] = None
    analysis_result: Optional[str] = None
    
    user: Optional[User] = Relationship(back_populates="train_sessions")
    stream: Optional["TrainSessionStream"] = Relationship(back_populates="session", cascade_delete=True)
    laps: List["TrainSessionLap"] = Relationship(back_populates="session", cascade_delete=True)
    

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
    executed_at: datetime = Field(default_factory=lambda : datetime.now(timezone.utc).replace(tzinfo=None),
                                  sa_column=Column(
                                        DateTime(timezone=True),  # ✅ tz-aware datetime
                                        onupdate=datetime.now(timezone.utc).replace(tzinfo=None)
                                    )
                                )
                                #   sa_column_kwargs={"onupdate": datetime.now(timezone.utc)}
                                #   )
    workout: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    coach_advice: Optional[str] = None

    user: Optional[User] = Relationship(back_populates="llms")
