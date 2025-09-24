from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_
from uuid import UUID
from typing import List
from datetime import datetime, timedelta, timezone

from infra.db.orm.models import LLM

from config.exceptions import DBError

# add / update
async def save_llm_predict(db:AsyncSession,
                          llm:LLM)->LLM:
    try:
        merged = await db.merge(llm)
        await db.commit()
        # await db.refresh(llm)
        return merged
    except Exception as e:
        await db.rollback()
        raise DBError(f"[save_llm_predict] failed id={llm.user_id}", e)

# read
async def get_llm_predict_by_user_id(db:AsyncSession,
                                     user_id:UUID)->LLM | None:
    try:
        res = await db.execute(
            select(LLM).where(LLM.user_id == user_id)
        )
        return res.scalar_one_or_none()


    except Exception as e:
        await db.rollback()
        raise DBError(f"[get_llm_predict_by_user_id] failed id={user_id}", e)

# delete 
async def delete_llm_predict_by_user_id(db:AsyncSession,
                                     llm:LLM)->None:
    try:
        db.delete(llm)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise DBError(f"[delete_llm_predict_by_user_id] failed id={llm.user_id}", e)
