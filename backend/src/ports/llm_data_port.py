from abc import ABC, abstractmethod
from uuid import UUID
from typing import List

from schemas.models import LLMResponse, LLMSessionResult


class LLMDataPort(ABC):

    
    @abstractmethod
    async def save_llm_result(self, user_id:UUID, 
                              llm_sessions:List[LLMSessionResult], 
                              advice:str)->LLMResponse :
        ...
        
    @abstractmethod
    async def get_llm_predict(self, user_id:UUID, )->LLMResponse :
        ...
        
    @abstractmethod
    async def is_llm_call_available(self, user_id:UUID) -> bool:
        ...