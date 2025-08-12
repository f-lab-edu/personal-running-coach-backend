from fastapi import APIRouter, Request, HTTPException, Depends
from starlette.responses import RedirectResponse
import urllib.parse
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.storage.session import get_session

from adapters.account_adapter import AccountAdapter
from adapters.token_adapter import TokenAdapter
from use_cases.auth.oauth_google import GoogleHandler
from config.settings import google

google_router = APIRouter(prefix="/google", tags=['auth-google'])

def get_handler(db:AsyncSession=Depends(get_session))->GoogleHandler:
    return GoogleHandler(
        account_adapter=AccountAdapter(db),
        token_adapter=TokenAdapter()
    )

@google_router.get("/login")
async def login_with_google():
    params = {
        "client_id": google.client_id,
        "redirect_uri": google.redirect_uri,
        "response_type": "code", 
        "scope": google.scope,
        "access_type": "offline",  # online 
        "prompt": "consent",
    }
    url = f"{google.auth_endpoint}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@google_router.get("/callback")
async def google_callback(request:Request,
                          google_handler:GoogleHandler = Depends(get_handler)):
    # get return code from google login
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="missing code")
    token = await google_handler.handle_login(auth_code=code)
    
    return token