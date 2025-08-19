from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from adapters import AccountAdapter, TokenAdapter
from schemas.models import AccountResponse, LoginResponse, TokenResponse
from config.exceptions import TokenExpiredError, TokenInvalidError
from config.logger import get_logger
from infra.db.storage import repo
from infra.security import encrypt_token
from config.settings import security

logger = get_logger(__file__)

class AuthHandler():
    """
    검증 핸들러.
    """
    def __init__(self, 
                 account_adapter:AccountAdapter, 
                 token_adapter:TokenAdapter,
                 db:AsyncSession
                 ):
        self.db = db
        self.account_adapter = account_adapter
        self.token_adapter = token_adapter
    
    
    async def login(self, email:str, pwd:str)->LoginResponse:
        """
        수동로그인 
        (아이디,비밀번호 미스매치) 실패시 401 에러
        """

        try:
            acct_response = await self.account_adapter.login_account(email, pwd)

            # 토큰 발급
            access = self.token_adapter.create_access_token(user_id=acct_response.id)
            refresh_result = self.token_adapter.create_refresh_token(user_id=acct_response.id)
            
            # 리프레시 토큰 암호화 저장
            encrypted = encrypt_token(data=refresh_result.token,
                                      key=security.encryption_key_refresh,
                                      token_type="account_refresh"
                                      )
            await repo.add_refresh_token(
                user_id=acct_response.id, token=encrypted, 
                expires_at=refresh_result.expires_at,
                db=self.db
            )
                
            return LoginResponse(
                token=TokenResponse(
                    access_token=access,
                    refresh_token=refresh_result.token
                ),
                user=acct_response
            )
            
        except HTTPException:
            raise

        except TokenInvalidError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        except Exception as e:
            logger.exception(str(e))
            raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")

        
    
    async def signup(self, email:str, pwd:str, name:str)->bool:
        """회원가입"""
        try:
            res = await self.account_adapter.create_account(email, pwd, name)
        except Exception as e:
            logger.exception(str(e))
            raise
        
        return True if res else False
    
    async def login_token(self, access:str)->LoginResponse:
        """토큰 로그인
            엑세스 토큰 유효시 입력 토큰 그대로 반환. 
            
            토큰 만료/오류시 401 Unauthorized 에러
            기타 에러 발생시 500 에러
        """
        try:
            # 액세스 토큰 검증
            access_payload = self.token_adapter.verify_access_token(access)

            # 액세스 토큰 유효. user_id 로 반환 사용자 정보 조회 
            user = await repo.get_user_by_id(user_id=access_payload.user_id,
                                db=self.db)

            return LoginResponse(
                user=AccountResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    provider=user.provider
                )
            ) 

        except HTTPException:
            raise
        except (TokenInvalidError, TokenExpiredError) as e: # 액세스 토큰 만료
            logger.exception(f"token expired: {e}")
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            logger.exception(f"token login error: {e}")
            raise HTTPException(status_code=500, detail=f"internal server error")
        
        
    async def refresh_token(self, refresh:str)->LoginResponse:
        """토큰 재발급
            클라이언트 리프레시토큰 검증
            리프레시토큰이 유효할 시 엑세스 토큰 새로 발급 후 로그인 처리
            
            토큰 만료/오류시 401 Unauthorized 에러
            기타 에러 발생시 500 에러
        """
        try:
            # 액세스 토큰 검증
            refresh_payload = self.token_adapter.verify_refresh_token(refresh)

            # 리프레시 토큰 db 대조
            valid = await self.account_adapter.validate_token_with_db(
                                        user_id=refresh_payload.user_id,
                                        refresh_token=refresh)
            # 토큰 not valid
            if not valid: 
                raise HTTPException(status_code=401, detail="refresh_token not valid")

            # 액세스토큰 재발급
            new_access = self.token_adapter.create_access_token(refresh_payload.user_id)
            
            # 유저정보 get 
            user = await repo.get_user_by_id(user_id=refresh_payload.user_id,
                                db=self.db)
            
            return LoginResponse(
                token=TokenResponse(
                    access_token=new_access,
                    refresh_token=refresh
                    ),
                user=AccountResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    provider=user.provider
                )
            )
        
        
        except HTTPException:
            raise
            
        # 잘못된 토큰, 토큰 만료
        except (TokenInvalidError, TokenExpiredError) as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
            
        except Exception as e:
            logger.exception(f"token login error: {e}")
            raise HTTPException(status_code=500, detail=f"internal server error")