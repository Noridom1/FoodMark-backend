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

@app.get("/test-supabase")
def test_supabase():
    data = supabase.table("Users").select("*").execute()
    return {"data": data.data}