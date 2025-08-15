from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from infra.db.orm.models import User, Token
from config.logger import get_logger

logger = get_logger(__name__)


## account
async def get_user_by_email(email: str,
                            db: AsyncSession) -> User | None:
    try:
        res = await db.execute(
            select(User).where(User.email == email)
        )
        return res.scalar_one_or_none()
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

        
async def add_user(user: User,
                   db: AsyncSession) -> None:
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def update_user(user: User,
                      db: AsyncSession) -> None:
    
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def delete_user(user: User,
                      db: AsyncSession) -> None:
    try:
        await db.delete(user)
        await db.commit()
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def get_refresh_token(user_id:UUID,
                            db:AsyncSession)-> str | None:
    try:
        res = await db.execute(
                        select(Token).where(Token.user_id==user_id))
        token = res.scalar_one_or_none()
        
        if token is None:
            return None
        return token.refresh_token
    
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def add_refresh_token(user_id:UUID, token:str,
                             db: AsyncSession) -> None:
    token = Token(user_id=user_id, refresh_token=token)

    try:
        db.add(token)
        await db.commit()
        await db.refresh(token)
    except Exception as e:
        logger.exception(str(e))
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))