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
    sns_connects: List["SNSConnect"] = Relationship(back_populates="user")
    train_sessions: List["TrainSession"] = Relationship(back_populates="user")
    llms: List["LLM"] = Relationship(back_populates="user")

class Token(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    refresh_token: str
    
    user: Optional[User] = Relationship(back_populates="tokens")

class SNSConnect(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    provider: str
    sns_id: str

    user: Optional[User] = Relationship(back_populates="sns_connects")

class TrainSession(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    train_date: datetime
    train_type: str
    train_detail: str


    user: Optional[User] = Relationship(back_populates="train_sessions")
    result: Optional["TrainResult"] = Relationship(back_populates="session")
    

class TrainResult(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: Optional[UUID] = Field(foreign_key="trainsession.id", nullable=False)
    stream_data1: Optional[str] = None  # json/text
    stream_data2: Optional[str] = None  # json/text TODO: 스트림데이터 저장 추후 업데이트
    analysis_result: Optional[str] = None
    
    session: Optional[TrainSession] = Relationship(back_populates="result")
    
class LLM(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    llm_type: str     #TODO: enum
    llm_result: str

    user: Optional[User] = Relationship(back_populates="llms")
