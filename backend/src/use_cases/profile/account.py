from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from config.logger import get_logger
from config.settings import security
from ports.account_port import AccountPort
from schemas.models import TokenPayload, UserInfoData, AccountResponse
# from infra.security import encrypt_token, decrypt_token, TokenInvalidError


logger = get_logger(__file__)



class AccountHandler:
    def __init__(self, db: AsyncSession, account_adapter: AccountPort):
        self.db = db
        self.account_adapter = account_adapter


    async def get_account_info(self, payload:TokenPayload)->AccountResponse:
        res = await self.account_adapter.get_account_by_id(user_id=payload.user_id)
        return res

    async def update_info(self, payload:TokenPayload, 
                          pwd:str=None, 
                          name:str=None,
                          user_info:UserInfoData=None)->AccountResponse:

        res = await self.account_adapter.update_account(user_id=payload.user_id,
                                                        pwd=pwd, name=name,
                                                        update_info=user_info
                                                        )
        return res