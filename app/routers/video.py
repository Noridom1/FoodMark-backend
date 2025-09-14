from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..services import video_service
from ..database import supabase
from fastapi import Form

router = APIRouter(prefix='/video', tags=['video'])

def run_add_user_video(url: str, user_id: str):
    data, error = video_service.add_user_video(url=url, user_id=user_id)
    if error:
        # log or handle internally
        print(f"Error processing video for {user_id}: {error}")
    else:
        print(f"Video processed successfully for {user_id}: {data}")

@router.post('/add_user_video')
async def download_video(
    url: str = Form(...),
    user_id: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    # enqueue background task
    background_tasks.add_task(run_add_user_video, url, user_id)

    # return immediately
    return {
        "status": "queued",
        "message": "Video will be processed in background"
    }