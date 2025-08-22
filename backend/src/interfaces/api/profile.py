from fastapi import APIRouter
from schemas.models import AccountResponse


router = APIRouter(prefix="/profile")

@router.put("/me")
async def update_info(data:AccountResponse):
    # 현재 사용자 정보 받기
    return

@router.put("/update")
async def update_info(data:AccountResponse):
    # 사용자 정보 업데이트
    return


@router.post("/sns-connect")
async def sns_connect(platform:str):
    # sns 연결 처리 (facebook, kakao 등)
    return

@router.post("/strava-connect")
async def strava_connect(strava_auth_code:str):
    # strava 연결
    return


@router.delete("/deactivate")
async def deactivate_account():
    # 계정 비활성화, (탈퇴)
    return