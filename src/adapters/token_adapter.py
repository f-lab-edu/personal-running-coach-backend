from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

from ports.token_port import TokenPort
from schemas.models import TokenPayload, TokenResponse
from config.logger import get_logger
from config import constants as con
from config.settings import token_config

logger = get_logger(__name__)
auth_scheme = HTTPBearer()

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
                                key=token_config.secret, 
                                algorithm=token_config.algorithm)
        except JWTError as e:
            logger.exception(f"jwt encoding error {e}")
            raise HTTPException(status_code=500, detail="error while creating token")
        
        token = TokenResponse(
            access_token=access,
            exp=expires,
        )
        
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
                                key=token_config.secret, 
                                algorithm=token_config.algorithm)
        except JWTError as e:
            logger.exception(f"jwt encoding error {e}")
            raise HTTPException(status_code=500, detail="error while creating token")
        
        # TODO: DB 에 refresh 토큰 저장

        token = TokenResponse(
            refresh_token=refresh,
            exp=expires,
        )
        
        return token


    def verify_access_token(self, cred:HTTPAuthorizationCredentials=Depends(auth_scheme)
                            )->TokenPayload: 
        
        now = int(datetime.now(timezone.utc).timestamp())
        token = cred.credentials
        try:
            payload = jwt.decode(token,
                                 key=token_config.secret,
                                 algorithms=token_config.algorithm
                                 )
            token = TokenPayload(**payload)
            
            ## token type check
            if token.token_type != "access":
                raise HTTPException(status_code=403, detail="Invalid token type")    
            elif token.exp < now :
                raise HTTPException(status_code=403, detail="token expired")

            return token
        
        except JWTError as e:
            logger.exception(f"Token verification error {e}")
            raise HTTPException(status_code=401, detail=f"invalid token")

        
    def verify_refresh_token(self, cred:HTTPAuthorizationCredentials=Depends(auth_scheme)
                            )->TokenPayload: 
        now = int(datetime.now(timezone.utc).timestamp())
        token = cred.credentials
        try:
            payload = jwt.decode(token,
                                 key=token_config.secret,
                                 algorithms=token_config.algorithm
                                 )
            token = TokenPayload(**payload)
            
            ## token type check
            if token.token_type != "refresh":
                raise HTTPException(status_code=403, detail="Invalid token type")    
            elif token.exp < now :
                raise HTTPException(status_code=403, detail="token expired")

            return token
        
        except JWTError as e:
            logger.exception(f"Token verification error {e}")
            raise HTTPException(status_code=401, detail=f"invalid token")
        
    ### 토큰 삭제
    def invalidate_refresh_token(self, jwt_str:str)->bool: 
        # TODO: db 에 저장된 토큰 삭제
        ...
    
    