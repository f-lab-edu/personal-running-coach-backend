from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_
from uuid import UUID
from typing import List
from datetime import datetime, timedelta, timezone

from infra.db.orm.models import LLM
from config.logger import get_logger

logger = get_logger(__name__)

# add / update
async def save_llm_predict(db:AsyncSession,
                          llm:LLM)->LLM:
    try:
        db.add(llm)
        await db.commit()
        await db.refresh(llm)
        return llm
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise

# read
async def get_llm_predict_by_user_id(db:AsyncSession,
                                     user_id:UUID)->LLM:
    try:
        res = await db.execute(
            select(LLM).where(LLM.user_id == user_id)
        )
        return res.scalar_one_or_none()


    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise

# delete 
async def delete_llm_predict_by_user_id(db:AsyncSession,
                                     llm:LLM)->None:
    try:
        db.delete(llm)
        await db.commit()

    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise