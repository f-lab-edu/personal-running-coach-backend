from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from ports.account_port import AccountPort
from schemas.models import AccountResponse, UserInfoData
from infra.db.orm.models import User, UserInfo
from infra.db.storage import repo
from infra.security import hash_password, verify_password, decrypt_token
from config.settings import security
from config.exceptions import InternalError, NotFoundError, ValidationError, CustomError

class AccountAdapter(AccountPort):
    def __init__(self,db:AsyncSession):
        self.db = db
    
    async def create_account(self, email: str, pwd: str, name: str, provider: str = "local") -> AccountResponse:
        """계정 생성. 
            일반 계정 생성과 외부 프로바이더 계정생성 모두 가능
        return: AccountResponse
        """
        try:
            # 기존 존재하는 유저인지 확인
            user = await repo.get_user_by_email(email=email, db=self.db)
            if user:
                raise ValidationError(detail=f"Email {email} already exist")
            
            # Hash password only for local accounts
            hashed_password = None
            if provider == "local":
                hashed_password = await hash_password(pwd)
            
            # Create new user
            new_user = User(
                email=email,
                hashed_pwd=hashed_password,
                name=name,
                provider=provider
            )
            
            await repo.save_user(new_user, self.db)
            
            return AccountResponse(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name,
                provider=new_user.provider
            )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error creating account", original_exception=e)
        
    async def get_account(self, email: str) -> AccountResponse:
        """이메일로 유저정보 조회"""
        try:
            # Get user from database
            user = await repo.get_user_by_email(email=email, db=self.db)
            if not user:
                raise NotFoundError(detail=f"User {email} not found")
            
            return AccountResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                provider=user.provider
            )
            
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error getting account", original_exception=e)
        
    async def get_account_by_id(self, user_id: UUID) -> AccountResponse:
        """사용자 ID로 유저정보 조회"""
        try:
            user = await repo.get_user_by_id(user_id=user_id, db=self.db)
            if not user:
                raise NotFoundError(detail=f"User {user_id} not found")
            info = await repo.get_user_info(user.id, db=self.db)
            return AccountResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                provider=user.provider,
                info=info
            )
        except ValueError as e:
            raise ValidationError(detail="Invalid user ID format", original_exception=e)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error get_account_by_id", original_exception=e)
    

    async def get_user_info_by_id(self, user_id:UUID)->UserInfoData : 
        try:
            return await repo.get_user_info(user_id=user_id,
                                            db=self.db)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error get_user_info_by_id", original_exception=e)



    async def login_account(self, email: str, pwd: str) -> AccountResponse:
        """
        이메일, 비밀번호를 사용한 일반 로그인
        return: AccountResponse
        """
        try:
            user = await repo.get_user_by_email(email=email, db=self.db)
            if not user:
                raise ValidationError(detail="Invalid email or password")
            is_valid = await verify_password(pwd, user.hashed_pwd)
            if not is_valid:
                raise ValidationError(detail="Invalid email or password")
            info = await repo.get_user_info(user_id=user.id, db=self.db)
            return AccountResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                provider=user.provider,
                info=info
            )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error login_account", original_exception=e)
        
    async def provider_login(self, email: str, provider: str, name: Optional[str] = None) -> AccountResponse:
        """OAuth provider login
            구글 로그인 등 외부 프로바이더 로그인.
            유저 테이블에 존재하지 않을 시 (새 로그인 시), 유저 생성 후 유저 리턴
            return: AccountResponse
        """
        try:
            user = await repo.get_user_by_email(email=email, db=self.db)
            if user:
                info = await repo.get_user_info(user.id, db=self.db)
                return AccountResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    provider=user.provider,
                    info=info
                )
            else:
                new_user = User(
                    email=email,
                    name=name,
                    provider=provider,
                    hashed_pwd=None  #provider 로그인 시 비밀번호 없음. (구글 등)
                )
                
                await repo.save_user(new_user, self.db)
                
                return AccountResponse(
                    id=new_user.id,
                    email=new_user.email,
                    name=new_user.name,
                    provider=new_user.provider
                )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error in provider login", original_exception=e)

    async def update_account(self, user_id:UUID, pwd: str, name: str, update_info:UserInfoData) -> AccountResponse:
        """
        유저 정보 업데이트
        비밀번호 변경시 provider 확인 (provider = local 일때만 비밀번호 해시 저장)
        """
        try:
            # db 에서 유저 확인
            user = await repo.get_user_by_id(user_id=user_id, db=self.db)
            if not user:
                raise NotFoundError(detail="User not found")
            
            if name is not None:
                user.name = name
            if pwd is not None and user.provider == "local":
                user.hashed_pwd = await hash_password(pwd)
            await repo.save_user(user=user, db=self.db)

            # info 업데이트
            info = await repo.get_user_info(user.id, self.db)
            if info is None:
                info = UserInfo(
                    user_id=user_id,
                    **update_info.model_dump(exclude_unset=True)
                )
            else:
                for field in UserInfoData.model_fields.keys():  
                    value = getattr(update_info, field)
                    if value is not None:
                        setattr(info, field, value)

            updated_info = await repo.save_user_info(user_info=info, db=self.db)

            return AccountResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                provider=user.provider,
                info=updated_info
            )
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error update login", original_exception=e)
        

    async def deactivate_account(self, email: str) -> bool:
        """계정 삭제"""
        try:
            # Find user by email
            user = await repo.get_user_by_email(email=email, db=self.db)
            if not user:
                raise NotFoundError(detail="User not found")
            
            #TODO: delete token  cascade??
            
            #TODO: delete sns connect
            
            # TODO: delete train session
            
            # Delete user
            await repo.delete_user(user=user, db=self.db)
            
            return True
        
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error deactivate_account", original_exception=e)
    
    async def validate_token_with_db(self, user_id:UUID, refresh_token:str,
                                     device_id:UUID
                                     )->bool:
        """db에 저장된 리프레시토큰과 클라이언트의 리프래시토큰 대조 검증"""
        try:
            db_refresh = await repo.get_refresh_token(db=self.db, user_id=user_id, device_id=device_id)
            
            # db 에 기존 refresh 없음
            if db_refresh is None:
                return False
            
            # 복호화
            decrypted = decrypt_token(token_encrypted= db_refresh, 
                                      key=security.encryption_key_refresh,
                                      token_type="account_refresh"
                                      )
            
            # 토큰 미스매치
            return decrypted == refresh_token
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error validate_token_with_db", original_exception=e)

    
    

    # # TODO: db 에 저장된 토큰 삭제
    async def remove_token(self, user_id:UUID, device_id:UUID)->bool: 
        try:
            res = await repo.remove_refresh_token(user_id=user_id,
                                                device_id=device_id,
                                                db=self.db)
            return res
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error remove_token", original_exception=e)
