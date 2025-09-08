from google import genai
import requests
from google.genai import types
from ..config import settings
from pydantic import BaseModel
from typing import List, Optional
import requests






class Dish(BaseModel):
    name: str
    price: str
    rating: Optional[float] = None   # e.g. 4.5
    taste: Optional[str] = None      # e.g. "spicy", "sweet and sour"


class Review(BaseModel):
    title: str
    rating: float                    # rating for the whole restaurant experience
    price: Optional[str] = None      # overall price range, e.g. "$$"
    comment: Optional[str] = None    # optional review text


class Restaurant(BaseModel):
    name: str
    address: Optional[str] = None
    dishes: List[Dish] = []
    reviews: List[Review] = []


def classify_video():
    client = genai.Client(api_key=settings.google_api_key)
    video_url = "https://fgkmsasdgcykscfcsynx.supabase.co/storage/v1/object/public/videobucket/@dianthoii__video_7474461317957520658.mp4"
    video_bytes = requests.get(video_url).content
    
    prompt = """
    You are given a video. Classify it into exactly one of the following categories:

    0 — Review Food Store: reviews or rates a restaurant, cafe, or food shop.
    1 — Cooking Guide: teaches or demonstrates how to cook or prepare food.
    2 — Mukbang: features someone eating large amounts of food, often while interacting with the audience.

    Respond with only the integer 0, 1, or 2 corresponding to the correct category. Do not include any other text.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
            ),
            types.Part(text=prompt)
        ]
        ),
        config={
        "response_mime_type": "application/json",
        "response_schema": int,
        }
    )
    print(response.text)
    return response


def summarize_video():
    client = genai.Client(api_key=settings.google_api_key)
    video_url = "https://fgkmsasdgcykscfcsynx.supabase.co/storage/v1/object/public/videobucket/@dianthoii__video_7474461317957520658.mp4"
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
        ),
        config={
        "response_mime_type": "application/json",
        "response_schema": list[Restaurant],
        }
    )
    print(response.text)
    get_distance("89-91 Nguyen Gia Tri, Binh Thanh")
    return response


def get_distance(address):
    url = "https://api.distancematrix.ai/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "OOV4afQIsa7SsVlWP1eF1RhrWZbJXA4HP1VTdvUhkqfvXg1cu2lHor0NmrCfASym"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data)   # full JSON
        # Example: extract latitude & longitude
        if data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            print(location)
    else:
        print("Error:", response.status_code, response.text)







