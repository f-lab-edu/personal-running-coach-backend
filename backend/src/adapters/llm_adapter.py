from ports.llm_port import LLMPort
from typing import List
from openai import AsyncOpenAI
import json

from schemas.models import UserInfoData, TrainResponse


class LLMAdapter(LLMPort):    
    def __init__(self, api_key:str):
        self.client = AsyncOpenAI(api_key=api_key)


        self.functions = [
            {
                "name": "generate_training_plan",
                "description": "사용자의 최근 훈련 기록과 목표를 기반으로 일주일 훈련 계획을 생성",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan": {
                            "type": "array",
                            "description": "일주일 훈련 계획",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "day": {"type": "string"},
                                    "workout_type": {"type": "string"},
                                    "distance_km": {"type": "number"},
                                    "pace": {"type": "string"},
                                    "notes": {"type": "string"},
                                },
                                "required": ["day", "workout_type", "distance_km"]
                            }
                        }
                    },
                    "required": ["plan"]
                }
            }
        ]

    def _preprocess_prompt(self, user_info:UserInfoData, 
                           training_sessions:List[TrainResponse]
                           ):
        """
        사용자 정보 + 최근 훈련 데이터를 요약해서 LLM에 넘길 프롬프트 생성
        """
        user_summary = (
            f"사용자 정보:\n"
            f"- 나이: {user_info.age}\n"
            f"- 성별: {user_info.sex}\n"
            f"- 키: {user_info.height}\n"
            f"- 몸무게: {user_info.weight}\n"
            f"- 목표: {user_info.train_goal}\n"
        )

        session_summary = "최근 훈련 세션:\n"
        for s in training_sessions:
            session_summary += (
                f"- 날짜: {s.train_date}, "
                f"거리: {s.distance}km, "
                f"시간: {s.total_time/60:.1f}분, "
                f"평균속도: {1000 / s.avg_speed} sec/km"
                f"훈련: {s.activity_title}, "
                f"분석결과: {s.analysis_result}\n"
            )

        return (
            f"{user_summary}\n"
            f"{session_summary}\n"
            "위 데이터를 참고하여 일주일 훈련 계획을 생성해줘."
        )
    

    async def generate_training_plan(self, user_info:UserInfoData, 
                               training_sessions:List[TrainResponse])->List[dict] :
        """
        Function calling을 통해 훈련 계획 생성
        """
        prompt = self._preprocess_prompt(user_info, training_sessions)

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",   # 또는 gpt-4.1, gpt-3.5 등 선택
            messages=[
                {"role": "system", "content": "너는 러닝 코치야."},
                {"role": "user", "content": prompt},
            ],
            functions=self.functions,
            function_call={"name": "generate_training_plan"},
        )

        message = response.choices[0].message
        if message.function_call:
            args = json.loads(message["function_call"]["arguments"])
            return args["plan"]

        return []
        

    async def generate_coach_advice(
        self,
        user_info: UserInfoData,
        training_sessions: List[TrainResponse],
    ) -> str:
        """
        일반 프롬프트로 코치 피드백 생성
        """
        prompt = self._preprocess_prompt(user_info, training_sessions)
        prompt += "\n위 훈련 데이터를 바탕으로 사용자의 현재 상태와 전반적인 코멘트를 작성해줘."

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 러닝 코치야."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message["content"]
