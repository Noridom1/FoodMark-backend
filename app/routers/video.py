from fastapi import APIRouter, HTTPException
from ..services import video_service
from ..database import supabase
from fastapi import Form

router = APIRouter(prefix='/video', tags=['video'])

@router.post('/add_user_video')
async def download_video(url: str = Form(...), user_id: str = Form(...)):
    data, error = video_service.add_user_video(url=url, user_id=user_id)
    print(error)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {
        "status": "success",
        "data": data
    }
