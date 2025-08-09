import pyktok as pyk
import os

def download_video_tiktok(url: str, save_dir: str):
    os.makedirs(save_dir, exist_ok=True)

    old_cwd = os.getcwd()
    try:
        os.chdir(save_dir)
        pyk.specify_browser('chrome')

        try:
            save_result = pyk.save_tiktok(
                url,
                save_video=True,
                metadata_fn='metadata.csv'
            )
            storage_path = os.path.join(save_dir, save_result['video_fn'])
            return storage_path, None
        except Exception as e:
            return None, e

    finally:
        os.chdir(old_cwd)