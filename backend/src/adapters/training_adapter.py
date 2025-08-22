from ports.training_port import *


class TrainingAdapter(TrainingPort):
    def save_session(self, token:str, session:TrainSession)->bool:
        ...
        
    def update_session(self, token:str, session_id:str, session:TrainSession)->TrainSession:
        ...
        
    def get_session_by_id(self, token:str, session_id:str)->TrainSession:
        ...
        
    def get_sessions_by_date(self, token:str, start_date:datetime, end_date:datetime)-> List[TrainSession]:
        ## datetime??
        ...
        
    def delete_session(self, token:str, session_id:str)->bool:
        ...
        
    def set_training_goal(self, token:str, training_goal:TrainGoal)->bool:
        ...
        
    def get_training_goal(self, token:str)->TrainGoal:
        ...
        
        