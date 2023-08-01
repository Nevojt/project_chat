from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client, Client
from gotrue.errors import AuthApiError


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# Create a random user login email and password.
email = "nevojt@gmail.com"
password = "nevojt88"
# user = supabase.auth.sign_up({"email": email, "password": password})  


# Sing in to user database
session = None
try:
    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
except AuthApiError:
    print("Authentification failed")



data = supabase.table("room_one").select("name", "message").execute()
print(data)

# out to session database
supabase.auth.sign_out()
