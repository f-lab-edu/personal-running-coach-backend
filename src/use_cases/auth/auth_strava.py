from fastapi import HTTPException
import httpx

from config.settings import strava
from adapters import StravaAdapter






class StravaHandler:
    def __init__(self, adapter: StravaAdapter):
        self.strava_adapter = adapter


    async def _get_token(self, code:str)->dict:
        """스트라바 토큰 받기"""
        payload = {
            "client_id": strava.client_id,
            "client_secret": strava.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(strava.token_url, data=payload)
        
        response.raise_for_status()
        return response.json()
    
        
    async def connect(self, code:str):
        """스트라바 토큰 저장"""
        
        # 토큰 받기
        token = await self._get_token(code)
    
        # TODO: 토큰 암호화
        
        # TODO: 토큰 저장