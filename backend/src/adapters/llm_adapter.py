"""LLM 서드파티 api 호출 아답터"""

from ports.llm_port import LLMPort
from typing import List
from openai import AsyncOpenAI, APIConnectionError, APIError, RateLimitError
import json

from schemas.models import UserInfoData, TrainResponse
from config.exceptions import InternalError, CustomError

class LLMAdapter(LLMPort):    
    def __init__(self, api_key:str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-5-nano"

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
            
        )
    

    async def generate_training_plan(self, user_info:UserInfoData, 
                               training_sessions:List[TrainResponse])->List[dict] :
        """
        Function calling을 통해 훈련 계획 생성
        """
        try:
            prompt = self._preprocess_prompt(user_info, training_sessions)
            prompt += "\n위 데이터를 참고하여 일주일 훈련 계획을 생성해줘."


            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "너는 러닝 코치야."},
                    {"role": "user", "content": prompt},
                ],
                functions=self.functions,
                function_call={"name": "generate_training_plan"},
            )

            message = response.choices[0].message
            if message.function_call:
                try:
                    args = json.loads(message.function_call.arguments)
                    plan = args.get("plan")
                    if not plan:
                        raise InternalError(context="LLM response missing 'plan'")
                    return args["plan"]
                except (KeyError, json.JSONDecodeError) as e:
                    raise InternalError(context="Invalid LLM function_call response", original_exception=e)

            return []

        except (APIConnectionError, RateLimitError, APIError) as e:
            raise InternalError(context="LLM error", original_exception=e)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error generate_training_plan", original_exception=e)

        

    async def generate_coach_advice(
        self,
        user_info: UserInfoData,
        training_sessions: List[TrainResponse],
    ) -> str:
        """
        일반 프롬프트로 코치 피드백 생성
        """
        try:
            prompt = self._preprocess_prompt(user_info, training_sessions)
            prompt += "\n위 훈련 데이터를 바탕으로 현재 사용자가 목표를 달성하기 위해서 잘하고 있는지 한문장으로 간략하게 평가해줘"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "너는 러닝 코치야."},
                    {"role": "user", "content": prompt},
                ],
            )

            return response.choices[0].message.content
    
        except (APIConnectionError, RateLimitError, APIError) as e:
            raise InternalError(context="LLM error", original_exception=e)
        except CustomError:
            raise
        except Exception as e:
            raise InternalError(context="Error generate_coach_advice", original_exception=e)
