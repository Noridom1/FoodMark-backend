# from fastapi import APIRouter, HTTPException
# from ..database import supabase

# router = APIRouter(prefix="test", tags=["test"])

# @router.get("/test-supabase")
# def test_supabase():
#     # Example: fetch from a table called 'users'
#     data = supabase.table("users").select("*").execute()
#     return {"data": data.data}