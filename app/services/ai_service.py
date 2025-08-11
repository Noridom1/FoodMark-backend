from google import genai
import requests
from google.genai import types
from ..config import settings

def summarize_video():
    # 1. Public Supabase Storage video URL
    client = genai.Client(api_key=settings.google_api_key)
    video_url = "https://fgkmsasdgcykscfcsynx.supabase.co/storage/v1/object/public/videobucket/@dianthoii__video_7474461317957520658.mp4"
    # 2. Download the video
    video_bytes = requests.get(video_url).content

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
            ),
            types.Part(text='Extract the information and the address of the place if needed')
        ]
        )
    )
    print(response.text)
    return response

