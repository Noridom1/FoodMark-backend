from fastapi import FastAPI
from .routers import auth, video
from .database import supabase

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
    

