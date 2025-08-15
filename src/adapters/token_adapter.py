from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

from ports.token_port import TokenPort
from schemas.models import TokenPayload, TokenResponse
from config.logger import get_logger
from config.exceptions import TokenExpiredError, TokenInvalidError
from config import constants as con
from config.settings import jwt_config

logger = get_logger(__name__)

class TokenAdapter(TokenPort):
    def __init__(self, access_token_exp:int=con.ACCESS_TOKEN_EXPIRE_MINUTES, 
                        refresh_token_exp:int=con.REFRESH_TOKEN_EXPIRE_DAYS
                 ):
        self.access_token_exp = access_token_exp
        self.refresh_token_exp = refresh_token_exp
    
    
    def create_access_token(self, user_id:str)->TokenResponse: 
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
            access = jwt.encode(payload.model_dump(mode='json'), 
                                key=jwt_config.secret, 
                                algorithm=jwt_config.algorithm)
        except JWTError as e:
            logger.exception(f"jwt encoding error {e}")
            raise TokenInvalidError(status_code=500, detail="error while creating token")
        
        token = TokenResponse(access_token=access)
        
        return token
        

    def create_refresh_token(self, user_id:str)->TokenResponse: 
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
            refresh = jwt.encode(payload.model_dump(mode='json'), 
                                key=jwt_config.secret, 
                                algorithm=jwt_config.algorithm)
        except JWTError as e:
            logger.exception(f"jwt encoding error {e}")
            raise TokenInvalidError(status_code=500, detail="error while creating token")

        token = TokenResponse(refresh_token=refresh)
        
        return token


    def verify_access_token(self, token_str:str)->TokenPayload: 
        
        now = int(datetime.now(timezone.utc).timestamp())
        try:
            payload = jwt.decode(token_str,
                                 key=jwt_config.secret,
                                 algorithms=jwt_config.algorithm
                                 )
            token = TokenPayload(**payload)
            
            ## token type check
            if token.token_type != "access":
                raise TokenInvalidError(status_code=401, detail="Invalid token type")    
            elif token.exp < now :
                raise TokenExpiredError(status_code=401, detail="token expired")

            return token
        
        except JWTError as e:
            logger.exception(f"Token verification error {e}")
            raise TokenInvalidError(status_code=401, detail=f"invalid token")

        
    def verify_refresh_token(self, token_str:str)->TokenPayload: 
        now = int(datetime.now(timezone.utc).timestamp())

        try:
            payload = jwt.decode(token_str,
                                 key=jwt_config.secret,
                                 algorithms=jwt_config.algorithm
                                 )
            token = TokenPayload(**payload)
            
            ## token type check
            if token.token_type != "refresh":
                raise TokenInvalidError(status_code=401, detail="Invalid token type")    
            elif token.exp < now :
                raise TokenExpiredError(status_code=401, detail="token expired")

            return token
        
        except JWTError as e:
            logger.exception(f"Token verification error {e}")
            raise TokenInvalidError(status_code=401, detail=f"invalid token")
        
    ### 토큰 삭제
    def invalidate_refresh_token(self, jwt_str:str)->bool: 
        # TODO: db 에 저장된 토큰 삭제
        ...
    
    