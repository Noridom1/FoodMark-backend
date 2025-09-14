from google import genai
import requests
from google.genai import types
from ..config import settings
from pydantic import BaseModel
from typing import List, Optional
import requests
from ..database import supabase
from geopy.distance import geodesic


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

class CookingStep(BaseModel):
    step_number: int
    title: str
    instruction: str


class CookingGuide(BaseModel):
    title: str
    summary: Optional[str] = None
    ingredients: List[str]
    steps: List[CookingStep]
 


class DishRecommendation(BaseModel):
    id: str
    name: str
    price: Optional[str] = None
    rating: Optional[float] = None
    taste: Optional[str] = None


class StoreRecommendation(BaseModel):
    id: str
    name: str
    address: str
    lat: float
    lng: float
    distance_km: float
    recommended_dishes: List[DishRecommendation]

class RouteRecommendation(BaseModel):
    route: List[StoreRecommendation]
    description: str


def classify_video(video_url):
    client = genai.Client(api_key=settings.google_api_key)
    # video_url = "https://fgkmsasdgcykscfcsynx.supabase.co/storage/v1/object/public/videobucket/@dianthoii__video_7474461317957520658.mp4"
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
    return int(response.text)


def summarize_video(type, video_url):
    if type == 0:
        schema = list[Restaurant]
        text_prompt = "Đây là một video về review những quán ăn, hãy trích xuất những thông tin về một hoặc nhiều quán ăn được nhắc đến trong video. Hãy trả lời bằng Tiếng Việt"
    else:
        schema = CookingGuide
        text_prompt = "Đây là một video về hướng dẫn nấu ăn. Hãy trích xuất những thông tin về món ăn và cách nấu: Tên món ăn, miêu tả món ăn, nguyên liệu, các bước nấu ăn. Hãy trả lời bằng Tiếng Việt"

    
    print(schema)
    client = genai.Client(api_key=settings.google_api_key)
    # video_url = "https://fgkmsasdgcykscfcsynx.supabase.co/storage/v1/object/public/videobucket/@dianthoii__video_7474461317957520658.mp4"
    video_bytes = requests.get(video_url).content
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
            ),
            types.Part(text=text_prompt)
        ]
        ),
        config={
        "response_mime_type": "application/json",
        "response_schema": schema,
        }
    )
    # print(response.text)
    # get_distance("89-91 Nguyen Gia Tri, Binh Thanh")
    # print(recommend_dish(user_id = "cbcf5839-9c3f-499a-b4a6-3302f734776c", user_lat=10, user_lng=104))
    return response.text


def get_distance(address):
    url = "https://api.distancematrix.ai/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "OOV4afQIsa7SsVlWP1eF1RhrWZbJXA4HP1VTdvUhkqfvXg1cu2lHor0NmrCfASym"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # print(data)   # full JSON
        # Example: extract latitude & longitude
        if data.get("result"):
            location = data["result"][0]["geometry"]["location"]
            print(location)
    else:
        print("Error:", response.status_code, response.text)


def get_location(address: str):
    url = "https://api.distancematrix.ai/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "OOV4afQIsa7SsVlWP1eF1RhrWZbJXA4HP1VTdvUhkqfvXg1cu2lHor0NmrCfASym"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        # print(data)   # full JSON
        # Example: extract latitude & longitude
        if data.get("result"):
            location = data["result"][0]["geometry"]["location"]
            return location # {'lat': 10.803837, 'lng': 106.71570589999999}
    else:
        print("Error:", response.status_code, response.text)
        return None



def recommend_dish(user_id: str, user_lat=None, user_lng=None):
    # Fetch stores from DB
    stores = (
        supabase
        .table("FoodStore")
        .select("*")
        .eq("user_id", user_id)
        .execute()
        .data
    )

    # Build prompt
    text_prompt = "Bạn là một trợ lý du lịch.\n"
    text_prompt += "Các quán ăn gần đây:\n"

    for store in stores:
        # Get dishes for this store
        dishes = (
            supabase.table("Dishes")
            .select("*")
            .eq("user_id", user_id)
            .eq("store_id", store["id"])
            .execute()
            .data
        )

        # Get store location
        store_location = get_location(store["address"])
        print(store['name'], store_location)
        if not store_location:
            continue
        store_lat, store_lng = store_location["lat"], store_location["lng"]

        # Compute distance
        distance_km = geodesic((user_lat, user_lng), (store_lat, store_lng)).km
        

        dish_str = "\n".join([
            f"  - {dish['dish_id']} | {dish['name']} | {dish.get('price','')} | {dish.get('rating','')} | {dish.get('taste','')}"
            for dish in dishes
        ]) if dishes else "Chưa có món ăn"

        text_prompt += (
            f"- {store['id']} | {store['name']} | {store['address']} | lat={store_lat} | lng={store_lng}"
            f"{round(distance_km, 2)} km\n"
            f"  Món ăn:\n{dish_str}\n"
        )

    text_prompt += "\nNhiệm vụ của bạn:\n"
    text_prompt += "1. Gợi ý một lộ trình tối ưu để ghé thăm các quán (có thể không cần đi tất cả).\n"
    text_prompt += "2. Ưu tiên khoảng cách ngắn trước, nhưng vẫn đảm bảo đa dạng món ăn.\n"
    text_prompt += "3. Trả về kết quả JSON theo schema sau:\n\n"
    text_prompt += """{
        "route": [
            {
                "id": "store_id",
                "name": "Tên quán",
                "address": "Địa chỉ",
                "lat": lat,
                "lng": lng
                "distance_km": 1.2,
                "recommended_dishes": [
                    {
                        "id": "dish_id",
                        "name": "Tên món",
                        "price": "100000",
                        "rating": 4.5,
                        "taste": "spicy"
                    }
                ]
            }
        ]
        "description": "Viết một đoạn hướng dẫn hấp dẫn cho người dùng theo lộ trình food tour này. Bắt đầu từ quán đầu tiên, chỉ dẫn người dùng cách đi tiếp từng quán, nhấn mạnh trải nghiệm ẩm thực tại mỗi điểm, hương vị đặc trưng của các món ăn, khoảng cách giữa các quán, và cảm giác khám phá từng món. Sử dụng ngôn từ sinh động, gợi hình ảnh, kích thích vị giác và tạo cảm giác như đang dẫn người dùng thực sự đi trải nghiệm chuyến food tour này."
    }"""

    # Call Gemini with schema enforcement
    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=text_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RouteRecommendation
        }
    )

    # Parse JSON into Pydantic model
    return RouteRecommendation.model_validate_json(response.text)