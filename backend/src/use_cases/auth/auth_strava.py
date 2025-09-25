from sqlalchemy.ext.asyncio import AsyncSession

from config.exceptions import CustomError, InternalError, NotFoundError, ValidationError
from config.settings import security
from adapters import StravaAdapter
from schemas.models import TokenPayload
from infra.security import encrypt_token, decrypt_token
from infra.db.storage.third_party_token_repo import (
    get_third_party_token_by_user_id,
    create_third_party_token,
    update_third_party_token
)



class StravaHandler:
    def __init__(self, db: AsyncSession, adapter: StravaAdapter):
        self.db = db
        self.strava_adapter = adapter

        
    async def connect(self, payload:TokenPayload, code:str)->dict:
        """초기 연결 및 재연결시 사용
            스트라바 액세스, 리프레시 토큰을 발급받아 db에 저장
            
            return: {"status": "ok" / "fail", "message": msg}
        """
        
        try:

            # 토큰 받기
            strava_token = await self.strava_adapter.connect(code)

            # 토큰 암호화
            # refresh_token, access_token, 
            encrypted_access = encrypt_token(data=strava_token.get("access_token"),
                                                key=security.encryption_key_strava,
                                                token_type="strava_access"
                                                )
            encrypted_refresh = encrypt_token(data=strava_token.get("refresh_token"),
                                                key=security.encryption_key_strava,
                                                token_type="strava_refresh"
                                                )
            
            if not payload:
                raise ValidationError(detail="User not authenticated")
            
            # 기존 토큰이 있는지 확인
            existing_token = await get_third_party_token_by_user_id(
                user_id=payload.user_id,
                provider="strava",
                db=self.db
            )
            
            if existing_token:
                # 기존 토큰이 있으면 업데이트
                await update_third_party_token(
                    user_id=payload.user_id,
                    provider="strava",
                    access_token=encrypted_access,
                    refresh_token=encrypted_refresh,
                    expires_at=strava_token.get("expires_at"),
                    db=self.db
                )
            else:
                # 기존 토큰이 없으면 생성
                await create_third_party_token(
                    user_id=payload.user_id,
                    provider="strava",
                    provider_user_id=str(strava_token.get("athlete", {}).get("id", "")),
                    access_token=encrypted_access,
                    refresh_token=encrypted_refresh,
                    expires_at=strava_token.get("expires_at"),
                    db=self.db
                )

            return {"status": "ok","msg":"Strava connected successfully"}
        
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error strava connect", original_exception=e)
        
        

    
        
    async def get_access_and_refresh_if_expired(self, payload:TokenPayload)->str:
            """ 
            현재 액세스 토큰 만료 검증.
            만료시 재발급 및 db 업데이트.
            유효 액세스 토큰 반환
                parameter: 
                    payload: 사용자 액세스 토큰 payload
                return: access_token (str)
            """
            
            try: 
                if not payload:
                    raise ValidationError(detail="User not authenticated")
            
                # 기존 토큰 get
                existing_token = await get_third_party_token_by_user_id(
                    user_id=payload.user_id,
                    provider="strava",
                    db=self.db
                )
                if not existing_token:
                    raise NotFoundError(detail="Strava token not found")
                
                # 토큰 검증
                if not await self.strava_adapter.is_token_expired(expires_at=existing_token.expires_at):
                    return decrypt_token(token_encrypted=existing_token.access_token,
                                  key=security.encryption_key_strava,
                                    token_type="strava_access"
                                  )

                # 토큰 만료시
                # 리프레시토큰으로 새 토큰 발급 받기
                decrypted_refresh = decrypt_token(token_encrypted=existing_token.refresh_token,
                                                  key=security.encryption_key_strava,
                                                    token_type="strava_access"
                                                  )
                strava_token = await self.strava_adapter.refresh_token(decrypted_refresh)

                # 토큰 암호화
                # refresh_token, access_token, 
                encrypted_access = encrypt_token(data=strava_token.get("access_token"),
                                                    key=security.encryption_key_strava,
                                                    token_type="strava_access"
                                                    )
                encrypted_refresh = encrypt_token(data=strava_token.get("refresh_token"),
                                                    key=security.encryption_key_strava,
                                                    token_type="strava_refresh"
                                                    )
                    # 기존 토큰 업데이트
                await update_third_party_token(
                    user_id=payload.user_id,
                    provider="strava",
                    access_token=encrypted_access,
                    refresh_token=encrypted_refresh,
                    expires_at=strava_token.get("expires_at"),
                    db=self.db
                )
                return strava_token.get('access_token')
            
            except CustomError:
                raise
            except Exception as e:
                raise InternalError(context="error get_access_and_refresh_if_expired", original_exception=e)
    
