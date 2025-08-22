from fastapi import APIRouter



router = APIRouter(prefix="/stats")


@router.get("/llm-pred")
async def llm_prediction():
    # 사용자 데이터 기반 고급 해석
    # 트렌드, 훈련 밸런스, 목표대비 진행률, 한줄 요약
    ...
    
@router.post("/calculations")
async def calculations(data:dict):
    # 수치 계산
    # 존분배율, 총달리기시간, 총 거리, 평균 페이스, 인터벌 현황
    ...