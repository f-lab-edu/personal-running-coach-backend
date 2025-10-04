from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from uuid import UUID

from config.exceptions import DBError
from infra.db.orm.models import User, UserInfo, Token


## account
async def get_user_by_email(email: str,
                            db: AsyncSession) -> User | None:
    try:
        res = await db.execute(
            select(User).where(User.email == email)
        )
        return res.scalar_one_or_none()
    except Exception as e:
        raise DBError(context=f"[get_user_by_email] failed {email}", original_exception=e)

async def get_user_by_id(user_id: UUID,
                         db: AsyncSession) -> User | None:
    try:
        res = await db.execute(
            select(User).where(User.id == user_id)
        )
        return res.scalar_one_or_none()
    except Exception as e:
        raise DBError(context=f"[get_user_by_id] failed id={user_id}", original_exception=e)

        
async def save_user(user: User,
                   db: AsyncSession) -> User:
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[save_user] failed id={user.id}", original_exception=e)



async def delete_user(user: User,
                      db: AsyncSession) -> None:
    try:
        await db.delete(user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[delete_user] failed id={user.id}", original_exception=e)

async def save_user_info(user_info:UserInfo,
                        db:AsyncSession)->UserInfo:
    try:
        db.add(user_info)
        await db.commit()
        await db.refresh(user_info)
        return user_info
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[save_user_info] failed id={user_info.user_id}", original_exception=e)

    
async def get_user_info(user_id:UUID,
                        db:AsyncSession)->UserInfo | None:
    try:
        res = await db.execute(
            select(UserInfo).where(UserInfo.user_id == user_id)
        )
        info = res.scalar_one_or_none()
        if info is None:
            return None
        return info 

    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[get_user_info] failed id={user_id}", original_exception=e)

async def get_refresh_token(user_id:UUID, device_id:UUID,
                            db:AsyncSession)-> str | None:
    try:
        res = await db.execute(
                        select(Token).where(and_(Token.user_id==user_id, 
                                                 Token.device_id == device_id)))
        token = res.scalar_one_or_none()
        
        if token is None:
            return None
        return token.refresh_token
    
    except Exception as e:
        raise DBError(context=f"[get_refresh_token] failed id={user_id}", original_exception=e)

# add/refresh refresh_token
async def save_refresh_token(user_id:UUID, 
                             device_id:UUID,
                            token:str,
                            expires_at: int,
                             db: AsyncSession) -> None:
    
    try:
        res = await db.execute(select(Token).where(and_(Token.user_id == user_id,
                                                        Token.device_id == device_id
                                                        )))
        refresh_token = res.scalar_one_or_none()
        if refresh_token:
            refresh_token.refresh_token = token
            refresh_token.expires_at = expires_at
        else:
            refresh_token = Token(user_id=user_id, 
                                  device_id=device_id,
                        refresh_token=token,
                        expires_at=expires_at
                        )
            db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
    except Exception as e:
        await db.rollback()
        raise DBError(context=f"[save_refresh_token] failed id={user_id}", original_exception=e)


async def remove_refresh_token(user_id:UUID, device_id:UUID,
                            db:AsyncSession):
    try:
        res = await db.execute(
            delete(Token).where(and_(Token.user_id==user_id, 
                                    Token.device_id == device_id)))
        
        await db.commit()
        if res.rowcount == 0:
            return False
        return True

    except Exception as e:
        raise DBError(context=f"[remove_refresh_token] failed id={user_id}", original_exception=e)
