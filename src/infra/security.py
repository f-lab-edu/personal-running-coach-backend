"""암호화/복호화 모듈

"""
import bcrypt
from cryptography.fernet import Fernet
from config.settings import security
from fastapi.concurrency import run_in_threadpool

fernet = Fernet(security.encryption_key.encode())

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


#토큰 암호화
def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

#토큰 복호화
def decrypt_token(token_encrypted: str) -> str:
    return fernet.decrypt(token_encrypted.encode()).decode()