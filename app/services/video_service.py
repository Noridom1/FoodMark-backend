from ..database import supabase
from ..utils import videos
import os
from ..services.ai_service import classify_video, summarize_video, get_location
import json
import re
import time

def add_user_video(url: str, user_id: str):
    """
    Downloads a video from the given URL and saves it to the storage.
    If the video already exists in the database, it does not download it again.
    Returns the video data if successful, or an error message if not.
    """

    user_existed = supabase.table("User").select("*").eq("id", user_id).execute()
    if not user_existed.data:
        return None, "User does not exist."

    video_existed = supabase.table("Video").select("*").eq("video_url", url).execute()
    if not video_existed.data:
        save_dir = os.path.join('storage', 'videos', 'downloaded')
        
        # Download video and upload to the bucket
        public_url, vid_desc, error = videos.download_video_sstik(url=url, save_dir=save_dir)

        # public_url, vid_desc, error = videos.download_video_tiktok(url=url, save_dir=save_dir)
        if error:
            print(f"Error downloading video: {error}")
            return None, error

        print("public_url:", public_url)

        # Process video
        vid_type = classify_video(public_url)
        time.sleep(2)
        video_info = summarize_video(type=vid_type, video_url=public_url)

        # Insert video to database
        result = supabase.table("Video").insert({
            # 'user_id': user_id,
            'type': vid_type,
            'description': vid_desc,
            'video_url': url,
            'bucket_url': public_url,
            'raw_info': video_info
        }).execute()

        video_id = result.data[0]['id'] if result.data else None



    else:
        print("[add_user_video] Video has already existed")
        video_id = video_existed.data[0]['id']
        vid_type = video_existed.data[0]['type']
        video_info = video_existed.data[0]['raw_info']

    user_video_existed = supabase.table("UserVideo").select("*").eq("user_id", user_id).eq("video_id", video_id).execute()

    if not user_video_existed:
        result = supabase.table("UserVideo").insert({
            'user_id': user_id,
            'video_id': video_id
        }).execute()

    else:
        result = user_video_existed

    if vid_type == 0: # Food Review
        add_foodstores(user_id, video_info)
    
    elif vid_type == 1: # Cooking Guide
        add_recipes(user_id, video_info)
        
    return result.data, None


def add_foodstores(user_id, video_info):
    print("Adding food store.")
    print(video_info)

    try:
        restaurants = json.loads(video_info)
    except json.JSONDecodeError as e:
        print("Failed to parse video_info:", e)
        return

    for r in restaurants:
        name = r.get("name")
        address = r.get("address", "")
        dishes = r.get("dishes", [])
        reviews = r.get("reviews", [])

        # --- Collect reviews into user_note ---
        comments = []
        for review in reviews:
            comment = review.get("comment")
            if comment:
                comments.append(f"- {comment}")
        user_note = "\n".join(comments) if comments else ""

        # --- Convert address -> lat/lng ---
        location = None
        if address:
            geo = get_location(address)
            if geo:
                lat, lng = geo["lat"], geo["lng"]
                location = f"POINT({lng} {lat})"  # WKT for PostGIS geography

        # --- Insert into FoodStore ---
        store_data = {
            "user_id": user_id,
            "name": name,
            "address": address,
            "location": location,
            "user_note": user_note,
        }

        store_res = supabase.table("FoodStore").insert(store_data).execute()
        if getattr(store_res, "error", None):
            print("Error inserting store:", store_res.error)
            continue

        store = store_res.data[0]
        store_id = store["id"]

        # --- Insert dishes ---
        for d in dishes:
            dish_name = d.get("name")
            price = d.get("price")

            price = parse_price(price)

            dish_data = {
                "user_id": user_id,
                "store_id": store_id,
                "name": dish_name,
                "price": price,
            }

            dish_res = supabase.table("Dishes").insert(dish_data).execute()
            if getattr(dish_res, "error", None):
                print("Error inserting dish:", dish_res.error)

    print("✅ All restaurants, dishes, and reviews inserted successfully.")


# def add_recipes(user_id, video_info):
#     print("Adding cooking recipe.")
#     print(video_info)

#     try:
#         cooking_guide = json.loads(video_info)
#     except json.JSONDecodeError as e:
#         print("Failed to parse video_info:", e)
#         return
    
#     name = cooking_guide.get('title')
#     summary = cooking_guide.get('summary')
#     ingredients = cooking_guide.get('ingredients')
#     cooking_steps = cooking_guide.get('steps')

#     ingre_list = []
#     for i in ingredients:
#         ingre = f"- {i}"
#         ingre_list.append(ingre)
    
#     formatted_ingredients = "\n".join(ingre_list) if ingre_list else ""

#     # --- Insert Cooking Guide ---
#     guide_data = {
#         "user_id": user_id,
#         "name": name,
#         "summary": summary,
#         "ingredients": formatted_ingredients,
#     }

#     guide_res = supabase.table("Recipe").insert(guide_data).execute()
#     if getattr(guide_res, "error", None):
#         print("Error inserting Recipe:", guide_res.error)
#         return
    
#     # --- Insert Cooking Steps ---
#     recipe = guide_res.data[0]
#     recipe_id = recipe["recipe_id"]

#     for step in cooking_steps:
#         step_number = step['step_number']
#         title = step['title']
#         instruction = step['instruction']

#         step_data = {
#             "user_id": user_id,
#             "recipe_id": recipe_id,
#             "step_number": step_number,
#             "title": title,
#             "instruction": instruction
#         }

#         step_res = supabase.table("CookingStep").insert(step_data).execute()
#         if getattr(step_res, "error", None):
#             print("Error inserting cooking step:", step_res.error)
#             continue

#     print("✅ The Cooking Guide with steps has been inserted successfully")

def add_recipes(user_id, video_info):
    print("Adding cooking recipe.")
    print(video_info)

    try:
        cooking_guide = json.loads(video_info)
    except json.JSONDecodeError as e:
        print("Failed to parse video_info:", e)
        return
    
    name = cooking_guide.get('title')
    summary = cooking_guide.get('summary')
    ingredients = cooking_guide.get('ingredients', [])
    cooking_steps = cooking_guide.get('steps', [])

    # Format ingredients into a string (same as before)
    ingre_list = [f"- {i}" for i in ingredients]
    formatted_ingredients = "\n".join(ingre_list) if ingre_list else ""

    # Call the Postgres function via RPC
    rpc_res = supabase.rpc("add_recipe_with_steps", {
        "p_user_id": user_id,
        "p_name": name,
        "p_summary": summary,
        "p_ingredients": formatted_ingredients,
        "p_steps": cooking_steps  # must be JSON (list of dicts)
    }).execute()

    if getattr(rpc_res, "error", None):
        print("❌ Error inserting recipe with steps:", rpc_res.error)
        return

    data = rpc_res.data
    print(f"✅ Inserted Recipe successfully (user_id={data['user_id']}, recipe_id={data['recipe_id']})")

def parse_price(price_str):
    if price_str is None:
        return None

    if isinstance(price_str, (int, float)):
        return int(price_str)  # already numeric

    # normalize string
    s = price_str.lower().strip()
    s = s.replace("đ", "").replace("vnd", "").replace(",", "").strip()

    # handle ranges like "50k-60k" → take average
    if "-" in s:
        parts = s.split("-")
        nums = [parse_price(p) for p in parts if p.strip()]
        nums = [n for n in nums if n is not None]
        if nums:
            return sum(nums) // len(nums)  # average
        return None

    # match numbers
    match = re.findall(r"[\d.]+", s)
    if not match:
        return None

    num = float(match[0])

    if "k" in s:
        return int(num * 1000)
    elif num < 1000:  
        # Example: "35" → assume "35k"
        return int(num * 1000)
    else:
        return int(num)

