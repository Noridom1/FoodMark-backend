from ..database import supabase
from ..utils import videos
import os

def add_user_video(url: str, user_id: str):
    """
    Downloads a video from the given URL and saves it to the storage.
    If the video already exists in the database, it does not download it again.
    Returns the video data if successful, or an error message if not.
    """

    user_existed = supabase.table("Users").select("*").eq("id", user_id).execute()
    if not user_existed.data:
        return None, "User does not exist."

    video_existed = supabase.table("Videos").select("*").eq("url", url).execute()
    if not video_existed.data:
        # return None, "Video already exists."
        save_dir = os.path.join('storage', 'videos', 'downloaded')
        storage_path, error = videos.download_video_sstik(url=url, save_dir=save_dir)
        if error:
            return None, error

        result = supabase.table("Videos").insert({
            # 'user_id': user_id,
            'url': url,
            'storage_path': storage_path
        }).execute()

        video_id = result.data[0]['id'] if result.data else None
    else:
        video_id = video_existed.data[0]['id']

    result = supabase.table("UserVideo").insert({
        'user_id': user_id,
        'video_id': video_id
    }).execute()    

    return result.data, None

