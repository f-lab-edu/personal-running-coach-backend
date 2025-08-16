from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import RedirectResponse
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession

from adapters import StravaAdapter
from infra.db.storage.session import get_session
from use_cases.auth.auth_strava import StravaHandler
from config.settings import strava

strava_router = APIRouter(prefix="/strava", tags=['auth-strava'])

def get_handler(db:AsyncSession=Depends(get_session))->StravaHandler:
    return StravaHandler(
        db=db,
        adapter=StravaAdapter(db)
    )

@strava_router.get("/connect")
async def connect_strava():
    params = {
        "client_id": strava.client_id,
        "redirect_uri": strava.redirect_uri,
        "response_type": "code", 
        "scope": strava.scope,
        "approval_prompt": "auto",
    }
    url = f"{strava.auth_endpoint}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@strava_router.get("/callback")
async def strava_callback(request:Request,
                          strava_handler:StravaHandler = Depends(get_handler))->dict:
    # get return code from google login
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="missing code")
    
    return await strava_handler.connect(code=code)
    