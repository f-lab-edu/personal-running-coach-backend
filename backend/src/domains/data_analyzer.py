from typing import List
from schemas.models import LapData, StreamData, ActivityData



class DataAnalyzer:
    def __init__(self):
        pass
    
    
    def classify_run_type(self, activity:ActivityData,
                          laps:List[LapData],
                          streams:List[StreamData]
                          ):
        """액티비티, 랩, 스트림 데이터 기반 훈련 타입 분류"""
        ...
        return 