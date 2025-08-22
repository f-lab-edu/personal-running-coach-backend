from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from schemas.models import TrainSession, TrainGoal

class TrainingPort(ABC):  ## TODO : TrainingSession MODEL
    @abstractmethod
    def save_session(self, token:str, session:TrainSession)->bool:
        ...
        
    @abstractmethod
    def update_session(self, token:str, session_id:str, session:TrainSession)->TrainSession:
        ...
        
    @abstractmethod
    def get_session_by_id(self, token:str, session_id:str)->TrainSession:
        ...
        
    @abstractmethod
    def get_sessions_by_date(self, token:str, start_date:datetime, end_date:datetime)-> List[TrainSession]:
        ## datetime??
        ...
        
    @abstractmethod
    def delete_session(self, token:str, session_id:str)->bool:
        ...
        
    @abstractmethod
    def set_training_goal(self, token:str, training_goal:TrainGoal)->bool:
        ...
        
    @abstractmethod
    def get_training_goal(self, token:str)->TrainGoal:
        ...
        
        