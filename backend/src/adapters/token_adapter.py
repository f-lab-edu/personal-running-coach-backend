from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from uuid import UUID

from ports.token_port import TokenPort
from schemas.models import TokenPayload, RefreshTokenResult
from config.logger import get_logger
from config.exceptions import TokenExpiredError, TokenInvalidError, CustomError, InternalError
from config import constants as con
from config.settings import jwt_config

logger = get_logger(__name__)

class TokenAdapter(TokenPort):
    def __init__(self, access_token_exp:int=con.ACCESS_TOKEN_EXPIRE_MINUTES, 
                        refresh_token_exp:int=con.REFRESH_TOKEN_EXPIRE_DAYS
                 ):
        self.access_token_exp = access_token_exp
        self.refresh_token_exp = refresh_token_exp
    
    
    def create_access_token(self, user_id:UUID)-> str:
        """액세스 jwt 토큰 생성. 

            return : jwt 문자열
        """ 
        try:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(minutes=self.access_token_exp)
            expires = int(expires.timestamp())
            payload = TokenPayload(
                user_id=user_id,
                exp=expires,
                iat=int(now.timestamp()),
                token_type="access"
            )
            try:
                # pydantic v2 에서는 mode='json' 으로 UUID 도 직렬화 됨.
                # v1 에서는 따로 uuid 직렬화 처리를 해줘야 함.
                access_jwt = jwt.encode(payload.model_dump(mode='json'), 
                                    key=jwt_config.secret, 
                                    algorithm=jwt_config.algorithm)
            except JWTError as e:
                raise InternalError(context="error while creating token")
            return access_jwt

        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error create_access_token ", original_exception=e)
        

    def create_refresh_token(self, user_id:UUID) -> RefreshTokenResult: 
        """리프레시 jwt 토큰 생성. 

            return : RefreshTokenResult
                token: jwt문자열
                expires_at: 타임스탬프 (int)
        """ 
        try:
            now = datetime.now(timezone.utc)
            expires = now + timedelta(days=self.refresh_token_exp)
            expires = int(expires.timestamp())
            payload = TokenPayload(
                user_id=user_id,
                exp=expires,
                iat=int(now.timestamp()),
                token_type="refresh"
            )
            try:
                refresh_jwt = jwt.encode(payload.model_dump(mode='json'), 
                                    key=jwt_config.secret, 
                                    algorithm=jwt_config.algorithm)
            except JWTError as e:
                raise InternalError(context="error while creating token", original_exception=e)
            return RefreshTokenResult(token=refresh_jwt, expires_at=expires)

        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error create_refresh_token", exception=e)


    def verify_access_token(self, token_str:str)->TokenPayload: 
        
        try:
            now = int(datetime.now(timezone.utc).timestamp())
            payload = jwt.decode(token_str,
                                 key=jwt_config.secret,
                                 algorithms=jwt_config.algorithm
                                 )
            token = TokenPayload(**payload)
            
            ## token type check
            if token.token_type != "access":
                raise TokenInvalidError(detail="Invalid token type")    
            elif token.exp < now :
                raise TokenExpiredError(detail="token expired")

            return token
        
        except ExpiredSignatureError:
            raise TokenExpiredError(detail=f"token expired")
        except JWTError as e:
            raise TokenInvalidError(detail=f"invalid token", original_exception=e)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error verify_access_token", original_exception=e)

        
    def verify_refresh_token(self, token_str:str)->TokenPayload: 

        try:
            now = int(datetime.now(timezone.utc).timestamp())
            payload = jwt.decode(token_str,
                                 key=jwt_config.secret,
                                 algorithms=jwt_config.algorithm
                                 )
            token = TokenPayload(**payload)
            
            ## token type check
            if token.token_type != "refresh":
                raise TokenInvalidError(detail="Invalid token type")    
            elif token.exp < now :
                raise TokenExpiredError(detail="token expired")

            return token
        except ExpiredSignatureError:
            raise TokenExpiredError(detail=f"token expired")
        except JWTError as e:
            raise TokenInvalidError(detail=f"invalid token", original_exception=e)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error verify_refresh_token", original_exception=e)
    
    def invalidate_refresh_token(self, jwt_str:str)->bool: 
        ### 토큰 삭제
        ...
    