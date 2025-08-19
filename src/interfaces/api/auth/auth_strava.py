from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import RedirectResponse
import urllib.parse

from sqlalchemy.ext.asyncio import AsyncSession
from use_cases.auth.dependencies import get_current_header
from infra.db.storage.session import get_session
from config.logger import get_logger
from config.exceptions import TokenError
from use_cases.auth.auth_strava import StravaHandler
from adapters import StravaAdapter, TokenAdapter
from config.settings import strava
from schemas.models import TokenPayload

strava_router = APIRouter(prefix="/strava", tags=['auth-strava'])
token_adapter = TokenAdapter()
logger = get_logger(__file__)


def get_handler(db:AsyncSession=Depends(get_session))->StravaHandler:
    return StravaHandler(
        strava_adapter=StravaAdapter(db),
    )

@strava_router.post("/connect")
async def connect_strava(
    access_jwt: TokenPayload = Depends(get_current_header)
):
    params = {
        "client_id": strava.client_id,
        "redirect_uri": strava.redirect_uri,
        "response_type": "code", 
        "scope": strava.scope,
        "approval_prompt": "auto",
        "state":access_jwt
    }
    url = f"{strava.auth_endpoint}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@strava_router.get("/callback")
async def strava_callback(request:Request,
                            strava_handler:StravaHandler = Depends(get_handler)):
    # get return code from google login
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="missing code")
    access_jwt = request.query_params.get("state")
    if not access_jwt:
        raise HTTPException(status_code=400, detail="missing token")

    
    try:
        payload = token_adapter.verify_access_token(access_jwt)
        res = await strava_handler.connect(
                            user_id=payload,
                            auth_code=code
                        )
        return res
        
    except HTTPException:
        raise
    except TokenError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")

    
