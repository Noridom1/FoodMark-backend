from ..database import supabase
from ..utils import videos
import os
from ..services.ai_service import classify_video

def add_user_video(url: str, user_id: str):
    """
    Downloads a video from the given URL and saves it to the storage.
    If the video already exists in the database, it does not download it again.
    Returns the video data if successful, or an error message if not.
    """

    user_existed = supabase.table("User").select("*").eq("id", user_id).execute()
    if not user_existed.data:
        return None, "User does not exist."

    video_existed = supabase.table("Video").select("*").eq("video_url", url).execute()
    if not video_existed.data:
        save_dir = os.path.join('storage', 'videos', 'downloaded')
        
        # Download video and upload to the bucket
        # storage_path, error = videos.download_video_sstik(url=url, save_dir=save_dir)
        public_url, vid_desc, error = videos.download_video_tiktok(url=url, save_dir=save_dir)
        if error:
            print(f"Error downloading video: {error}")
            return None, error

        print("public_url:", public_url)

        # Process video
        vid_type = classify_video(public_url)

        # Insert video to database
        result = supabase.table("Video").insert({
            # 'user_id': user_id,
            'type': vid_type,
            'description': vid_desc,
            'video_url': url,
            'bucket_url': public_url,
        }).execute()

        video_id = result.data[0]['id'] if result.data else None
    else:
        video_id = video_existed.data[0]['id']

    user_video_existed = supabase.table("UserVideo").select("*").eq("user_id", user_id).eq("video_id", video_id).execute()

    if not user_video_existed:
        result = supabase.table("UserVideo").insert({
            'user_id': user_id,
            'video_id': video_id
        }).execute()

    else:
        result = user_video_existed

    return result.data, None

