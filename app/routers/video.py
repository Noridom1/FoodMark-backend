from fastapi import APIRouter, HTTPException
from ..services import video_service
from ..database import supabase

router = APIRouter(prefix='/video', tags=['video'])

@router.post('/download_video')
async def download_video(url: str):
    data, error = video_service.download_video(url=url)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {
        "status": "success",
    }