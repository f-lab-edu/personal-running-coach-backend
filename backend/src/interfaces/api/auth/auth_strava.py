from fastapi import APIRouter, HTTPException, Depends, Body
from starlette.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import urllib.parse

from use_cases.auth.dependencies import get_current_user, validate_current_user
from infra.db.storage.session import get_session
from config.logger import get_logger
from config.exceptions import CustomError
from use_cases.auth.auth_strava import StravaHandler
from adapters import StravaAdapter, TokenAdapter
from config.settings import strava
from schemas.models import TokenPayload

strava_router = APIRouter(prefix="/strava", tags=['auth-strava'])
token_adapter = TokenAdapter()
logger = get_logger(__name__)

def get_handler(db:AsyncSession=Depends(get_session))->StravaHandler:
    return StravaHandler(
        db=db,
        adapter=StravaAdapter(db),
    )

@strava_router.get("/connect")
async def connect_strava(valid: bool = Depends(validate_current_user)):
    try:
        params = {
            "client_id": strava.client_id,
            "redirect_uri": strava.redirect_uri,
            "response_type": "code", 
            "scope": strava.scope,
            "approval_prompt": "auto",
        }
        url = f"{strava.auth_endpoint}?{urllib.parse.urlencode(params)}"
        # return RedirectResponse(url)
        return {"url":url}
    
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"connect_strava. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@strava_router.post("/callback")
async def strava_callback(code:str = Body(..., embed=True),
                        payload: TokenPayload = Depends(get_current_user),
                        strava_handler:StravaHandler = Depends(get_handler)):
    # get return code from google login
    if not code:
        raise HTTPException(status_code=400, detail="missing code")
    if not payload:
        raise HTTPException(status_code=400, detail="missing token")

    try:
        res = await strava_handler.connect(
                            payload=payload,
                            code=code
                        )
        return res
        
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"strava_callback. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
