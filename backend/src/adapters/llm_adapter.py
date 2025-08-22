from ports.llm_port import *

## TODO import from llm_client

class LLMAdapter(LLMPort):    
    def generate_training_plan(self, token:str, training_session:List[TrainSession] )->List[TrainSession]  :
        # TODO: trainingSession Model
        ...
        
    def generate_coach_advice(self, token:str, training_sessions:List[TrainSession])->CoachAdvice :
        # TODO: trainingSession Model
        ...
        
