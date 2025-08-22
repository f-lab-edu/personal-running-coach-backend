from abc import ABC, abstractmethod

class StatCalcPort(ABC):
    @abstractmethod
    def calc_zone_distrib(self):
        ...
        
    @abstractmethod
    def calc_weekly_efficiency(self):
        ...
        
    @abstractmethod
    def calc_trend(self):
        ...
        
    @abstractmethod
    def predict_race_time(self):
        ...
        