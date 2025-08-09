from ..database import supabase
from ..utils import videos
import os

def download_video(url: str, user_id: str):
    save_dir = os.path.join('storage', 'videos', 'downloaded')
    storage_path, error = videos.download_video_tiktok(url=url, save_dir=save_dir)
    if error:
        return error

    result = supabase.table("Videos").insert({
        'user_id': user_id,
        'url': url,
        'storage_path': storage_path
    }).execute()

    return result.data, None

