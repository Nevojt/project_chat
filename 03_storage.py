from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client, Client



url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# get file
# resp = supabase.storage.from_("image_bucket").get_public_url("wallpaper.jpg")
# print(resp)


#  Not Download
# resp = supabase.storage.from_("image_bucket").download("Picture.png")
# print(resp)                                       