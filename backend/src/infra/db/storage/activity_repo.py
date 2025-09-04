from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from infra.db.orm.models import TrainSession, TrainSessionStream, TrainSessionLap
from config.logger import get_logger

logger = get_logger(__name__)

# --- TrainSession ---
async def add_train_session(train_session: TrainSession, db: AsyncSession) -> TrainSession:
    try:
        db.add(train_session)
        await db.commit()
        await db.refresh(train_session)
        return train_session
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def get_train_session_by_id(session_id: UUID, db: AsyncSession) -> TrainSession | None:
    try:
        res = await db.execute(select(TrainSession).where(TrainSession.id == session_id))
        return res.scalar_one_or_none()
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

async def get_train_sessions_by_user(user_id: UUID, db: AsyncSession) -> list[TrainSession]:
    try:
        res = await db.execute(select(TrainSession).where(TrainSession.user_id == user_id))
        return res.scalars().all()
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

async def update_train_session(train_session: TrainSession, db: AsyncSession) -> TrainSession:
    try:
        db.add(train_session)
        await db.commit()
        await db.refresh(train_session)
        return train_session
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def delete_train_session(train_session: TrainSession, db: AsyncSession) -> None:
    try:
        await db.delete(train_session)
        await db.commit()
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# --- TrainSessionStream ---
async def add_train_session_stream(stream: TrainSessionStream, db: AsyncSession) -> TrainSessionStream:
    try:
        db.add(stream)
        await db.commit()
        await db.refresh(stream)
        return stream
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def get_train_session_stream(session_id: UUID, db: AsyncSession) -> TrainSessionStream | None:
    try:
        res = await db.execute(select(TrainSessionStream).where(TrainSessionStream.session_id == session_id))
        return res.scalar_one_or_none()
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

async def update_train_session_stream(stream: TrainSessionStream, db: AsyncSession) -> TrainSessionStream:
    try:
        db.add(stream)
        await db.commit()
        await db.refresh(stream)
        return stream
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def delete_train_session_stream(stream: TrainSessionStream, db: AsyncSession) -> None:
    try:
        await db.delete(stream)
        await db.commit()
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# --- TrainSessionLap ---
async def add_train_session_lap(lap: TrainSessionLap, db: AsyncSession) -> TrainSessionLap:
    try:
        db.add(lap)
        await db.commit()
        await db.refresh(lap)
        return lap
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def get_train_session_laps(session_id: UUID, db: AsyncSession) -> list[TrainSessionLap]:
    try:
        res = await db.execute(select(TrainSessionLap).where(TrainSessionLap.session_id == session_id))
        return res.scalars().all()
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

async def get_train_session_lap_by_id(lap_id: UUID, db: AsyncSession) -> TrainSessionLap | None:
    try:
        res = await db.execute(select(TrainSessionLap).where(TrainSessionLap.id == lap_id))
        return res.scalar_one_or_none()
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

async def update_train_session_lap(lap: TrainSessionLap, db: AsyncSession) -> TrainSessionLap:
    try:
        db.add(lap)
        await db.commit()
        await db.refresh(lap)
        return lap
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

async def delete_train_session_lap(lap: TrainSessionLap, db: AsyncSession) -> None:
    try:
        await db.delete(lap)
        await db.commit()
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))