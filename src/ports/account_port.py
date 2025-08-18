from abc import ABC, abstractmethod
from schemas.models import AccountResponse

class AccountPort(ABC):
    
    @abstractmethod
    def create_account(self, email:str, pwd:str, name:str)->AccountResponse:  
        ...
        
    @abstractmethod
    def get_account(self, email:str)->AccountResponse : 
        ...
        
    @abstractmethod
    def login_account(self, email:str, pwd:str)->AccountResponse : 
        ...
        
    @abstractmethod
    def update_account(self, token:str, acct_response:str)->AccountResponse : 
        ...
        
    @abstractmethod
    def provider_login(self, email:str, pwd:str)->AccountResponse : 
        ...
        
    @abstractmethod
    def deactivate_account(self, email:str)->bool : 
        ...
        