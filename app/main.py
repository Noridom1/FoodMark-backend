from fastapi import FastAPI
from .routers import auth
from .database import supabase

app = FastAPI()

# Register routers
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.get("/test-supabase")
def test_supabase():
    # Example: fetch from a table called 'users'
    data = supabase.table("Users").select("*").execute()
    return {"data": data.data}