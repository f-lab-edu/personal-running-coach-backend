from sqlalchemy.ext.asyncio import AsyncSession


from ports.account_port import AccountPort
from schemas.models import TokenPayload, UserInfoData, AccountResponse
from config.exceptions import DBError, InternalError, CustomError


class AccountHandler:
    def __init__(self, db: AsyncSession, account_adapter: AccountPort):
        self.db = db
        self.account_adapter = account_adapter


    async def get_account_info(self, payload:TokenPayload)->AccountResponse:
        try:
            res = await self.account_adapter.get_account_by_id(user_id=payload.user_id)
            return res
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error get_account_info", original_exception=e)


    async def update_info(self, payload:TokenPayload, 
                          pwd:str=None, 
                          name:str=None,
                          user_info:UserInfoData=None)->AccountResponse:
        try:
            res = await self.account_adapter.update_account(user_id=payload.user_id,
                                                            pwd=pwd, name=name,
                                                            update_info=user_info
                                                            )
            return res
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="error update_info", original_exception=e)