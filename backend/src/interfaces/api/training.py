from fastapi import APIRouter
from schemas.models import TrainSession


router = APIRouter(prefix="/training")


@router.put("/{session_id}", response_model=TrainSession)
async def edit_schedule(session_id:str, session_data:TrainSession):
    ...

@router.post("/upload-training", response_model=TrainSession)
async def upload_training(session_data:TrainSession):
    ...
