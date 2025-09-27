from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from schemas.models import TokenPayload, AccountRequest
from adapters import AccountAdapter
from infra.db.storage.session import get_session
from use_cases.profile.account import AccountHandler
from use_cases.auth.dependencies import get_current_user, get_test_user
from config.logger import get_logger
from config.exceptions import CustomError
logger = get_logger(__name__)

router = APIRouter(prefix="/profile", tags=['profile'])



def get_handler(db:AsyncSession=Depends(get_session))->AccountHandler:
    return AccountHandler(
        db=db,
        account_adapter=AccountAdapter(db=db)
    )

@router.get("/me")
async def get_info(
    payload: TokenPayload = Depends(get_current_user),
    handler:AccountHandler=Depends(get_handler)
    ):
    try:
        return await handler.get_account_info(payload=payload)
    except CustomError as e:
        if e.original_exception:
            logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"get_info. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.put("/update")
async def update_info(
    data:Optional[AccountRequest] = None,
    payload: TokenPayload = Depends(get_current_user),
    handler:AccountHandler=Depends(get_handler)
    ):
     
    try:
        return await handler.update_info(payload=payload, 
                            name=data.name, 
                            pwd=data.pwd, 
                            user_info=data.info)
    except CustomError as e:
        logger.exception(f"{e.context} {str(e.original_exception)}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.exception(f"update_info. {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# TODO
@router.post("/sns-connect")
async def sns_connect(platform:str):
    # sns 연결 처리 (facebook, kakao 등)
    return


@router.delete("/deactivate")
async def deactivate_account():
    # 계정 비활성화, (탈퇴)
    return