"""암호화/복호화 모듈

"""
import bcrypt
from cryptography.fernet import Fernet, InvalidToken
from fastapi.concurrency import run_in_threadpool

from config.settings import security
from config.exceptions import TokenInvalidError, InternalError



# bcrypt = 단방향 해시
# 비밀번호 해시 후 솔트와 함께 저장.
def _hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=security.bcrypt_rounds)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 확인시 checkpw 로 암호문 비교 체크
def _verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# threadpool 로 loop 블로킹 피하기
async def hash_password(pwd:str)->str:
    return await run_in_threadpool(_hash_password, pwd)

async def verify_password(pwd:str, hashed:str)->bool:
    return await run_in_threadpool(_verify_password, pwd, hashed)


# 공통 암호화 함수
def encrypt_token(data: str, key: bytes, token_type:str = None) -> str:
    try:
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()
    except Exception as e:
        raise InternalError(context="Token encryption failed", original_exception=e)

# 공통 복호화 함수
def decrypt_token(token_encrypted: str, key: bytes, token_type:str = None) -> str:
    fernet = Fernet(key)
    try:
        return fernet.decrypt(token_encrypted.encode()).decode()
    except InvalidToken as e:
        raise TokenInvalidError(detail="Invalid token", original_exception=e)
    except Exception as e:
        raise InternalError(context="Token decryption failed", original_exception=e)
