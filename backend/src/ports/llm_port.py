from abc import ABC, abstractmethod
from typing import List

from schemas.models import UserInfoData, TrainResponse


class LLMPort(ABC):

    @abstractmethod
    def _preprocess_prompt(self, user_info:UserInfoData, 
                           training_session:List[TrainResponse]
                           ):
        ...
    
    @abstractmethod
    async def generate_training_plan(self, user_info:UserInfoData, 
                               training_sessions:List[TrainResponse])->List[dict] :
        ...
        
    @abstractmethod
    async def generate_coach_advice(self, user_info:UserInfoData, 
                               training_sessions:List[TrainResponse])->str :
        ...
        
