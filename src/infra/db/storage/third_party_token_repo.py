from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from infra.db.orm.models import ThirdPartyToken
from config.logger import get_logger

logger = get_logger(__name__)


## third party token functions
async def create_third_party_token(
    user_id: UUID,
    provider: str,
    provider_user_id: str,
    access_token: str,
    refresh_token: str,
    expires_at: int,
    db: AsyncSession
) -> ThirdPartyToken:
    """서드파티 토큰을 생성하고 저장합니다."""
    try:
        token = ThirdPartyToken(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        
        db.add(token)
        await db.commit()
        await db.refresh(token)
        
        logger.info(f"{provider} token created for user {user_id}")
        return token
        
    except IntegrityError as e:
        await db.rollback()
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def get_third_party_token_by_user_id(
    user_id: UUID,
    provider: str,
    db: AsyncSession
) -> Optional[ThirdPartyToken]:
    """사용자 ID와 프로바이더로 토큰을 조회합니다."""
    try:
        res = await db.execute(
            select(ThirdPartyToken).where(
                ThirdPartyToken.user_id == user_id,
                ThirdPartyToken.provider == provider
            )
        )
        return res.scalar_one_or_none()
        
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def get_third_party_token_by_provider_user_id(
    provider: str,
    provider_user_id: str,
    db: AsyncSession
) -> Optional[ThirdPartyToken]:
    """프로바이더와 프로바이더 사용자 ID로 토큰을 조회합니다."""
    try:
        res = await db.execute(
            select(ThirdPartyToken).where(
                ThirdPartyToken.provider == provider,
                ThirdPartyToken.provider_user_id == provider_user_id
            )
        )
        return res.scalar_one_or_none()
        
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def update_third_party_token(
    user_id: UUID,
    provider: str,
    access_token: str,
    refresh_token: str,
    expires_at: int,
    db: AsyncSession
) -> Optional[ThirdPartyToken]:
    """서드파티 토큰을 업데이트합니다."""
    try:
        await db.execute(
            update(ThirdPartyToken).where(
                ThirdPartyToken.user_id == user_id,
                ThirdPartyToken.provider == provider
            ).values(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at
            )
        )
        
        await db.commit()
        
        # 업데이트된 토큰 반환
        return await get_third_party_token_by_user_id(user_id, provider, db)
        
    except Exception as e:
        await db.rollback()
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def delete_third_party_token(
    user_id: UUID,
    provider: str,
    db: AsyncSession
) -> bool:
    """사용자의 서드파티 토큰을 삭제합니다."""
    try:
        result = await db.execute(
            delete(ThirdPartyToken).where(
                ThirdPartyToken.user_id == user_id,
                ThirdPartyToken.provider == provider
            )
        )
        
        await db.commit()
        
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"{provider} token deleted for user {user_id}")
            return True
        else:
            logger.warning(f"No {provider} token found to delete for user {user_id}")
            return False
            
    except Exception as e:
        await db.rollback()
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def get_all_tokens_by_provider(
    provider: str,
    db: AsyncSession
) -> List[ThirdPartyToken]:
    """특정 프로바이더의 모든 토큰을 조회합니다."""
    try:
        res = await db.execute(
            select(ThirdPartyToken).where(
                ThirdPartyToken.provider == provider
            )
        )
        return res.scalars().all()
        
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def get_all_user_tokens(
    user_id: UUID,
    db: AsyncSession
) -> List[ThirdPartyToken]:
    """사용자의 모든 서드파티 토큰을 조회합니다."""
    try:
        res = await db.execute(
            select(ThirdPartyToken).where(
                ThirdPartyToken.user_id == user_id
            )
        )
        return res.scalar_one_or_none()
        
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))


async def is_third_party_connected(
    user_id: UUID,
    provider: str,
    db: AsyncSession
) -> bool:
    """사용자가 특정 서드파티 서비스에 연결되어 있는지 확인합니다."""
    try:
        token = await get_third_party_token_by_user_id(user_id, provider, db)
        return token is not None
        
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
