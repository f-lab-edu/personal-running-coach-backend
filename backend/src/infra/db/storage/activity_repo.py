from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_
from uuid import UUID
from typing import List
from datetime import datetime

from infra.db.orm.models import TrainSession, TrainSessionStream, TrainSessionLap
from schemas.models import ActivityData, LapData, StreamData
from config.exceptions import DBError

# --- TrainSession ---
async def add_train_session(db: AsyncSession,
                            user_id:UUID, 
                            activity:ActivityData,
                            ) -> TrainSession:
    try:

        session = TrainSession(
            user_id=user_id,
            provider=activity.provider,
            train_date=activity.start_date,
            distance=activity.distance,
            avg_speed=activity.average_speed,
            total_time = activity.elapsed_time,
            activity_title=activity.activity_title,
            analysis_result=activity.analysis_result
        )
        
        db.add(session)
        await db.commit()  ## increment + add 한번에 커밋
        await db.refresh(session)
        return session
    except IntegrityError as e:
        await db.rollback()
        return None
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[add_train_session] failed id={user_id}", original_exception=e)
    
async def get_train_session_by_date( db: AsyncSession, 
                                    user_id:UUID,
                                    start_date:datetime = None
                                    ) -> List[TrainSession] | None:
    try:

        result = await db.execute(
            select(TrainSession)
            .where(TrainSession.user_id == user_id, 
                   TrainSession.train_date >= start_date
                   )
            .order_by(TrainSession.train_date)
            )
        
        return result.scalars().all()
        
        
    except Exception as e:
        raise DBError(context=f"[get_train_session_by_date] failed id={user_id}", original_exception=e)

async def get_train_session_by_id(session_id: UUID, db: AsyncSession) -> TrainSession | None:
    try:
        res = await db.execute(
            select(TrainSession).where(TrainSession.id == session_id)
            )
        return res.scalar_one_or_none()
    except Exception as e:
        raise DBError(context=f"[get_train_session_by_id] failed id={session_id}", original_exception=e)

async def get_train_sessions_by_user(user_id: UUID, db: AsyncSession) -> list[TrainSession]:
    try:
        res = await db.execute(select(TrainSession).where(TrainSession.user_id == user_id))
        return res.scalars().all()
    except Exception as e:
        raise DBError(context=f"[get_trin_sessions_by_user] failed id={user_id}", original_exception=e)

async def update_train_session(train_session: TrainSession, db: AsyncSession) -> TrainSession:
    try:
        db.add(train_session)
        await db.commit()
        await db.refresh(train_session)
        return train_session
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[update_train_session] failed activity_id={train_session.activity_id}", original_exception=e)


async def delete_train_session(train_session: TrainSession, db: AsyncSession) -> None:
    try:
        await db.delete(train_session)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[delete_train_session] failed activity_id={train_session.activity_id}", original_exception=e)

# --- TrainSessionStream ---
async def add_train_session_stream(db: AsyncSession, session_id:UUID, stream:StreamData) -> TrainSessionStream:
    try:
        # stream 데이터 json 형식으로 변환
        data = TrainSessionStream(
            session_id=session_id,
            heartrate=stream.heartrate,
            cadence=stream.cadence,
            distance=stream.distance,
            velocity=stream.velocity,
            altitude=stream.altitude
        )
        
        db.add(data)
        await db.commit()
        await db.refresh(data)
        return data
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[add_train_session_stream] failed activity_id={session_id}", original_exception=e)

async def get_train_session_stream(user_id:UUID, session_id: UUID, db: AsyncSession) -> TrainSessionStream :
    try:

        check = await db.execute(
            select(TrainSession)
            .where(
                and_(TrainSession.user_id == user_id, TrainSession.id == session_id))
            )
        valid = check.scalar_one_or_none()
        if not valid: # user id sessionid mismatch
            raise DBError(context=f"invalid session id {session_id}", original_exception=None)


        res = await db.execute(select(TrainSessionStream).where(TrainSessionStream.session_id == session_id))
        return res.scalar_one_or_none()
    except Exception as e:
        raise DBError(context=f"[get_train_session_stream] failed session_id={session_id}", original_exception=e)

async def update_train_session_stream(stream: TrainSessionStream, db: AsyncSession) -> TrainSessionStream:
    try:
        db.add(stream)
        await db.commit()
        await db.refresh(stream)
        return stream
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[update_train_session_stream] failed session_id={stream.session_id}", original_exception=e)

async def delete_train_session_stream(stream: TrainSessionStream, db: AsyncSession) -> None:
    try:
        await db.delete(stream)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[delete_train_session_stream] failed session_id={stream.session_id}", original_exception=e)

# --- TrainSessionLap ---
async def add_train_session_lap(db: AsyncSession, session_id:UUID, laps: List[LapData]) -> List[TrainSessionLap]:
    try:
        rows = [
            TrainSessionLap(
                session_id=session_id,
                lap_index=lap.lap_index,
                distance=lap.distance,
                elapsed_time=lap.elapsed_time,
                average_speed=lap.average_speed,
                max_speed=lap.max_speed,
                average_heartrate=lap.average_heartrate,
                max_heartrate=lap.max_heartrate,
                average_cadence=lap.average_cadence,
                elevation_gain=lap.elevation_gain
            )
            for lap in laps
        ]
        
        
        
        db.add_all(rows)
        await db.commit()


    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[add_train_session_lap] failed session_id={session_id}", original_exception=e)

async def get_train_session_laps(user_id:UUID, session_id: UUID, db: AsyncSession) -> list[TrainSessionLap]:
    try:
        check = await db.execute(
            select(TrainSession)
            .where(
                and_(TrainSession.user_id == user_id, TrainSession.id == session_id))
            )
        valid = check.scalar_one_or_none()
        if not valid: # user id sessionid mismatch
            raise DBError(context="invalid session id", original_exception=None)

        res = await db.execute(
            select(TrainSessionLap)
            .where(TrainSessionLap.session_id == session_id)
            )
        return res.scalars().all()
    except Exception as e:
        raise DBError(context=f"[get_train_session_laps] failed session_id={session_id}", original_exception=e)

async def get_train_session_lap_by_id(lap_id: UUID, db: AsyncSession) -> TrainSessionLap | None:
    try:
        res = await db.execute(select(TrainSessionLap).where(TrainSessionLap.id == lap_id))
        return res.scalar_one_or_none()
    except Exception as e:
        raise DBError(context=f"[get_train_session_lap_by_id] failed lap_id={lap_id}", original_exception=e)

async def update_train_session_lap(lap: TrainSessionLap, db: AsyncSession) -> TrainSessionLap:
    try:
        db.add(lap)
        await db.commit()
        await db.refresh(lap)
        return lap
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[update_train_session_lap] failed lap_id={lap.id}", original_exception=e)

async def delete_train_session_lap(lap: TrainSessionLap, db: AsyncSession) -> None:
    try:
        await db.delete(lap)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[delete_train_session_lap] failed lap_id={lap.id}", original_exception=e)