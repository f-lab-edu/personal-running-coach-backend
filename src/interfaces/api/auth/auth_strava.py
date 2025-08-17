from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import RedirectResponse
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession

from adapters import StravaAdapter
from infra.db.storage.session import get_session
from use_cases.auth.auth_strava import StravaHandler
from config.settings import strava
from config.logger import get_logger

logger = get_logger(__name__)
strava_router = APIRouter(prefix="/strava", tags=['auth-strava'])

def get_handler(db:AsyncSession=Depends(get_session))->StravaHandler:
    return StravaHandler(
        db=db,
        adapter=StravaAdapter(db)
    )

@strava_router.get("/connect")
async def connect_strava():
    logger.info("Strava connect endpoint called")
    params = {
        "client_id": strava.client_id,
        "redirect_uri": strava.redirect_uri,
        "response_type": "code", 
        "scope": strava.scope,
        "approval_prompt": "auto",
    }
    url = f"{strava.auth_endpoint}?{urllib.parse.urlencode(params)}"
    logger.info(f"Redirecting to Strava auth: {strava.auth_endpoint}")
    return RedirectResponse(url)


@strava_router.get("/callback")
async def strava_callback(request:Request,
                          strava_handler:StravaHandler = Depends(get_handler))->dict:
    logger.info("Strava callback endpoint called")
    logger.info(f"Query params: {dict(request.query_params)}")
    
    # get return code from strava login
    code = request.query_params.get("code")
    if not code:
        logger.error("Missing code parameter in Strava callback")
        raise HTTPException(status_code=400, detail="missing code")
    
    logger.info(f"Received code from Strava: {code[:10]}...")
    
    try:
        result = await strava_handler.connect(code=code)
        logger.info("Strava callback completed successfully")
        return result
    except Exception as e:
        logger.exception(f"Error in Strava callback: {str(e)}")
        raise
    