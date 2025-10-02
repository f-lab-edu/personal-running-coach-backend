from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from schemas.models import AccountResponse, UserInfoData



class AccountPort(ABC):
    
    @abstractmethod
    async def create_account(self, email:str, pwd:str, name:str, provider: str)->AccountResponse:  
        ...
        
    @abstractmethod
    async def get_account(self, email:str)->AccountResponse : 
        ...

    @abstractmethod
    async def get_account_by_id(self, user_id:UUID)->AccountResponse : 
        ...

    @abstractmethod
    async def get_user_info_by_id(self, user_id:UUID)->UserInfoData : 
        ...
        
    @abstractmethod
    async def login_account(self, email:str, pwd:str)->AccountResponse : 
        ...
        
    @abstractmethod
    async def provider_login(self, email:str, provider: str, name: Optional[str] = None)->AccountResponse : 
        ...
        
    @abstractmethod
    async def update_account(self, user_id:UUID, pwd: str, name: str, update_info:UserInfoData)->AccountResponse : 
        ...
        
    @abstractmethod
    async def deactivate_account(self, email:str)->bool : 
        ...
    
    @abstractmethod
    async def validate_token_with_db(self, user_id:UUID, device_id:UUID, refresh_token:str)->bool:
        ...

    @abstractmethod
    async def remove_token(self, user_id:UUID, device_id:UUID)->bool: 
        ...