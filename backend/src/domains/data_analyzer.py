import numpy as np
from statistics import mean, pstdev, median
from typing import List, Optional, Dict

from schemas.models import LapData, StreamData, ActivityData



class DataAnalyzer:
    def __init__(self, max_hr:int=190, pace_gap_thr:float=120.0):
        self.max_hr = max_hr # 최대심박수
        self.pace_gap_threshold = pace_gap_thr    
    
    
    def _get_hr_percent(self, activity: ActivityData) -> Optional[float]:
        """심박 계산 (백분율)"""
        if not activity.average_heartrate:
            return None
        return (activity.average_heartrate / self.max_hr) * 100
    
    def _format_pace(self, speed: float) -> str:
        if not speed or speed <= 0:
            return "-"
        pace_sec = 1000 / speed  # 초/km
        minutes = int(pace_sec // 60)
        seconds = int(pace_sec % 60)
        return f"{minutes}'{seconds:02d}\"/km"
    
    def _to_pace(self, speed: float) -> float:
        """평균 속도(m/s) → 페이스(sec/km)"""
        if not speed:
            return float("inf")
        return 1000 / speed

    
    
    def analyze(self,
                activity:ActivityData,
                laps:List[LapData],
                stream:StreamData)->Dict[str, str]:
        """데이터 분석
        
        return {title: "", detail:""}
        """
        
        
        # 순서대로 탐색 (우선순위 있음)
        res = (
            self._classify_intervals(laps)
            or self._classify_tempo(activity, laps)
            or self._classify_speed_run(activity, laps)
            or self._classify_jogging(activity, laps)
            or self._classify_long_run(activity)
            or self._classify_recovery(activity, laps)
            or self._classify_default(activity)
        )

        return res
    
    
    
    # ------------------------
    # 인터벌
    # ------------------------
    def _classify_intervals(self, laps: List[LapData]) -> Optional[Dict[str, str]]:
        if not laps or len(laps) < 4:
            return None

        n = len(laps)
        lap_paces = [self._to_pace(lap.average_speed) for lap in laps]

        # 빠른랩 + 느린랩 후보 페어
        candidate_pairs = []
        for i in range(n - 1):
            fast, slow = lap_paces[i], lap_paces[i + 1]
            if fast == float("inf") or slow == float("inf"):
                continue
            if slow - fast >= self.pace_gap_threshold:
                candidate_pairs.append(i)

        if not candidate_pairs:
            return None

        # 연속된 페어 그룹 찾기
        groups = []
        cur = [candidate_pairs[0]]
        for idx in candidate_pairs[1:]:
            if idx - cur[-1] == 2:  # step=2 (fast+rec 반복)
                cur.append(idx)
            else:
                groups.append(cur)
                cur = [idx]
        groups.append(cur)

        # 가장 긴 그룹 선택
        best_group = max(groups, key=len)
        if len(best_group) < 2:
            return None

        # 반복 구간만 선택
        fast_laps = [laps[i] for i in best_group]
        easy_laps = [laps[i + 1] for i in best_group]

        # 대표 거리 / 평균 페이스
        rep_distance = round(mean([lap.distance for lap in fast_laps]), -1)
        avg_pace_str = self._format_pace(mean([lap.average_speed for lap in fast_laps]))

        # 리커버리
        avg_rec_dist = mean([lap.distance for lap in easy_laps])
        avg_rec_time = mean([lap.elapsed_time for lap in easy_laps])
        if len(easy_laps) > 1 and pstdev([lap.distance for lap in easy_laps]) < 0.1 * avg_rec_dist:
            recovery = f"리커버리 {int(round(avg_rec_dist, -1))}m {int(round(avg_rec_time))}초"
        else:
            recovery = f"리커버리 평균 {int(round(avg_rec_time))}초"

        reps = len(fast_laps)

        return {
            "title": f"{int(rep_distance)}m 인터벌 x {reps}회",
            "detail": f"{int(rep_distance)}m 평균 페이스 {avg_pace_str}, {recovery}, 총 {reps}회 반복"
        }
    # ------------------------
    # 템포런 (Zone 3-4, 6-15km, 일정 페이스)
    # ------------------------
    def _classify_tempo(self, activity: ActivityData, laps: List[LapData]) -> Optional[Dict[str, str]]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance or not activity.elapsed_time:
            return None
        
        speeds = [lap.average_speed for lap in laps if lap.average_speed]
        variability = pstdev(speeds) if len(speeds) > 1 else 0

        if 6 <= activity.distance/1000 <= 15 and 75 <= hr_pct <= 85 and variability < 0.3:
            km = round(activity.distance / 1000, 1)
            mins = round(activity.elapsed_time / 60)
            return {
                "title": f"{km}km 템포런",
                "detail": f"총 {km}km, {mins}분, 평균 심박 {activity.average_heartrate}bpm "
                          f"({int(hr_pct)}%), 평균 페이스 {self._format_pace(activity.average_speed)}"
            }
        return None

    # ------------------------
    # LSD (Zone 2, ≥15km)
    # ------------------------
    def _classify_long_run(self, activity: ActivityData) -> Optional[Dict[str, str]]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance or not activity.elapsed_time:
            return None
        
        if activity.distance/1000 >= 15 and 65 <= hr_pct <= 75:
            km = round(activity.distance / 1000, 1)
            mins = round(activity.elapsed_time / 60)
            return {
                "title": f"{km}km LSD",
                "detail": f"총 {km}km, {mins}분, 평균 심박 {activity.average_heartrate}bpm "
                          f"({int(hr_pct)}%), 평균 페이스 {self._format_pace(activity.average_speed)}"
            }
        return None

    # ------------------------
    # 스피드런 (Zone 4-5, 3-10km)
    # ------------------------
    def _classify_speed_run(self, activity: ActivityData, laps: List[LapData]) -> Optional[Dict[str, str]]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance or not activity.elapsed_time:
            return None
        
        if 3 <= activity.distance/1000 <= 10 and hr_pct >= 85:
            km = round(activity.distance / 1000, 1)
            mins = round(activity.elapsed_time / 60)
            return {
                "title": f"{km}km 스피드런",
                "detail": f"총 {km}km, {mins}분, 평균 심박 {activity.average_heartrate}bpm "
                          f"({int(hr_pct)}%), 평균 페이스 {self._format_pace(activity.average_speed)}"
            }
        return None

    # ------------------------
    # 조깅 (Zone 1-2, ≤8km)
    # ------------------------
    def _classify_jogging(self, activity: ActivityData, laps: List[LapData]) -> Optional[Dict[str, str]]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance or not activity.elapsed_time:
            return None
        if 40 <= hr_pct <= 75:
            km = round(activity.distance / 1000, 1)
            mins = round(activity.elapsed_time / 60)
            return {
                "title": f"{km}km {mins}분 조깅",
                "detail": f"평균 심박 {activity.average_heartrate}bpm ({int(hr_pct)}%), "
                        f"평균 페이스 {self._format_pace(activity.average_speed)}"
            }
        return None
    
    # ------------------------
    # 기본 분류 (거리 + 시간 러닝)
    # ------------------------
    def _classify_default(self, activity: ActivityData) -> Optional[Dict[str, str]]:
        if not activity.distance or not activity.elapsed_time:
            return {"title": "러닝", "detail": "세부 데이터를 확인할 수 없습니다."}
        
        km = round(activity.distance / 1000, 1)
        mins = round(activity.elapsed_time / 60)
        return {
            "title": f"{km}km {mins}분 러닝",
            "detail": f"총 거리 {km}km, 총 시간 {mins}분. 평균페이스 {self._format_pace(activity.average_speed)}"
        }
    
    # ------------------------
    # 리커버리 런 (Zone1-2, 3-8km, 느린 페이스)
    # ------------------------
    def _classify_recovery(self, activity: ActivityData, laps: List[LapData]) -> Optional[Dict[str, str]]:
        hr_pct = self._get_hr_percent(activity)
        if not hr_pct or not activity.distance or not activity.elapsed_time:
            return None

        distance_km = activity.distance / 1000
        avg_pace_sec = activity.elapsed_time / distance_km if distance_km > 0 else None  # 초/km

        if 2 <= distance_km <= 8 and hr_pct <= 50 :
            pace_min = int(avg_pace_sec // 60)
            pace_sec = int(avg_pace_sec % 60)
            return {
                'title': f"{int(distance_km)}km 회복런",
                'detail':f"평균 페이스 {pace_min}:{pace_sec:02d}/km"
            }
        return None