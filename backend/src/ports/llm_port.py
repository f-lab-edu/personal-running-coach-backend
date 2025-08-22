from abc import ABC, abstractmethod
from typing import List
from schemas.models import TrainSession, CoachAdvice


class LLMPort(ABC):
    
    @abstractmethod
    def generate_training_plan(self, token:str, training_sessions:List[TrainSession])->List[TrainSession] :
        # TODO: trainingSession Model
        ...
        
    @abstractmethod
    def generate_coach_advice(self, token:str, training_session:List[TrainSession])->CoachAdvice :
        # TODO: trainingSession Model
        ...
        
