from fastapi import FastAPI
from .routers import auth, video
from .database import supabase
from .services import ai_service
from .services import map_service
from fastapi import FastAPI, Form
from fastapi import Query
from typing import List
from fastapi import Body


app = FastAPI()


# Register routers
app.include_router(auth.router)
app.include_router(video.router)


@app.get("/")
def root():
    return {"message": "Backend is running!"}


@app.get("/current_user")
def test_supabase():
    # Example: fetch from a table called 'users'
    response = supabase.auth.get_user()
    return response

@app.get("/bucket/{name}")
def get_a_bucket(name: str):
    buckets = supabase.storage.list_buckets()
    
    print(buckets)

@app.get("/summarize")
def summarize_video():
    data = ai_service.summarize_video(
        type=1,
        video_url="https://fgkmsasdgcykscfcsynx.supabase.co/storage/v1/object/public/videobucket/BaChiXotTac.mp4"
    )

    print(data)
    
    return {
        "status": "success",
        "data": data
    }


@app.get('/classifier')
def classify_video():
    ai_service.classify_video(
        video_url="https://plsnwavugnuoppecuogh.supabase.co/storage/v1/object/public/videos/ComLuoi.mp4"
    )


@app.post("/foodtour/recommend")
def get_recommendation(
    user_id: str = Form(...),
    user_lat: float = Form(...),
    user_lng: float = Form(...)
):
    result = ai_service.recommend_dish(user_id=user_id, user_lat=user_lat, user_lng=user_lng)
    print(result)
    # return {
    #     "status": "success",
    #     "data": result
    # }
    return result




@app.post("/foodtour/route")
def get_route(points: list[tuple[float, float]] = Body(...)):
    gps_points = map_service.get_directions(points)
    return gps_points