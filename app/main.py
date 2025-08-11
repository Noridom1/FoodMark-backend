from fastapi import FastAPI
from .routers import auth
from .database import supabase
from .services import ai_service
app = FastAPI()

# Register routers
app.include_router(auth.router)
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
    ai_service.summarize_video()


@app.get('/classifier')
def classify_video():
    ai_service.classify_video()
