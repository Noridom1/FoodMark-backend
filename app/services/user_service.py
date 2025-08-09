from ..database import supabase
# from ..utils.security import hash_password, verify_password

def create_user(data):
    existing = supabase.table("Users").select("*").eq("username", data.username).execute()

    if existing.data:
        return None, "Username already exists"
    
    # hashed_pw = hash_password(data.password)
    result = supabase.table("Users").insert({**data.dict(), "password": data.password}).execute()
    return result.data, None

# def authenticate_user(username, password):
#     user_data = supabase.table("Users").select("*").eq("username", username).execute()
#     if not user_data.data:
#         return None
#     user = user_data.data[0]