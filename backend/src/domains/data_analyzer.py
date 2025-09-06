import numpy as np
from statistics import mean, pstdev

from typing import List, Optional
from schemas.models import LapData, StreamData, ActivityData, AnalysisResult



class DataAnalyzer:
    def __init__(self, max_hr:int=190):
        self.max_hr = max_hr # 최대심박수
    
    
    def _get_hr_percent(self, activity: ActivityData) -> Optional[float]:
        if not activity.average_heartrate:
            return None
        return (activity.average_heartrate / self.max_hr) * 100
    
    
    def analyze(self,
                activity:ActivityData,
                laps:List[LapData],
                stream:StreamData)->str:
        
        
        # 순서대로 탐색 (우선순위 있음)
        res = (
            self._classify_intervals(laps)
            or self._classify_hill_intervals(laps)
            or self._classify_tempo(activity, laps)
            or self._classify_speed_run(activity, laps)
            or self._classify_jogging(activity, laps)
            or self._classify_long_run(activity)
            or "분류 불가"
        )

        return res
    
    
    
    def _classify_intervals(laps: List[LapData]) -> Optional[str]:
        if not laps:
            return None

        avg_speed = mean([lap.average_speed for lap in laps])
        std_speed = pstdev([lap.average_speed for lap in laps]) if len(laps) > 1 else 0

        # 빠른 랩 = 평균보다 std 이상 빠른 랩
        hard_laps = [lap for lap in laps if lap.average_speed > avg_speed + 0.5 * std_speed]
        if len(hard_laps) < 2:
            return None  # 인터벌 아님

        # 반복 거리 평균
        hard_distances = [round(lap.distance) for lap in hard_laps]
        rep_distance = round(mean(hard_distances), -1)  # 10m 단위 반올림

        # 휴식 랩 추출 (빠른 랩 바로 뒤의 구간)
        recovery_laps = []
        for lap in laps:
            if lap in hard_laps:
                idx = laps.index(lap)
                if idx + 1 < len(laps):
                    recovery_laps.append(laps[idx + 1])

        # 휴식 특성 파악
        if recovery_laps:
            rec_distances = [lap.distance for lap in recovery_laps]
            rec_times = [lap.elapsed_time for lap in recovery_laps]

            # 거리 기반 or 시간 기반 선택
            if pstdev(rec_distances) < 0.1 * mean(rec_distances):  # 거의 일정하면 거리 회복
                recovery = f"{round(mean(rec_distances), -1)}m 리커버리"
            else:
                recovery = f"{round(mean(rec_times))}초 휴식"
        else:
            recovery = "자유 휴식"

        reps = len(hard_laps)
        return f"{rep_distance}m 인터벌 {recovery} x {reps}회"
    
    def _classify_hill_intervals(laps: List[LapData]) -> Optional[str]:
        hill_laps = [lap for lap in laps if lap.elevation_gain and lap.elevation_gain > 10]
        if len(hill_laps) < 2:
            return None
        rep_distance = round(mean([lap.distance for lap in hill_laps]), -1)
        reps = len(hill_laps)
        return f"{rep_distance}m 언덕 인터벌 x {reps}회"
    
    # ------------------------
    # 템포런 (Zone 3-4, 6-15km, 일정 페이스)
    # ------------------------
    def _classify_tempo(self, activity: ActivityData, laps: List[LapData]) -> Optional[str]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance:
            return None
        speeds = [lap.average_speed for lap in laps if lap.average_speed]
        variability = pstdev(speeds) if len(speeds) > 1 else 0

        if 6 <= activity.distance/1000 <= 15 and 75 <= hr_pct <= 85 and variability < 0.3:
            return f"{int(activity.distance/1000)}km 템포런"
        return None
    
     # ------------------------
    # LSD (Zone 2, ≥15km)
    # ------------------------
    def _classify_long_run(self, activity: ActivityData) -> Optional[str]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance:
            return None
        if activity.distance/1000 >= 15 and 65 <= hr_pct <= 75:
            return f"{int(activity.distance/1000)}km LSD"
        return None

    # ------------------------
    # 스피드런 (Zone 4-5, 3-10km)
    # ------------------------
    def _classify_speed_run(self, activity: ActivityData, laps: List[LapData]) -> Optional[str]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance:
            return None
        if 3 <= activity.distance/1000 <= 10 and hr_pct >= 85:
            return f"{int(activity.distance/1000)}km 스피드런"
        return None

    # ------------------------
    # 조깅 (Zone 1-2, ≤8km)
    # ------------------------
    def _classify_jogging(self, activity: ActivityData, laps: List[LapData]) -> Optional[str]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance:
            return None
        if activity.distance/1000 <= 8 and hr_pct <= 70:
            return f"{int(activity.distance/1000)}km 조깅"
        return None