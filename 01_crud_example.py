from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client, Client
from datetime import datetime, timedelta
import time


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)





# insert data to database 
def insert_data():
    supabase.table("room_one").insert(
        {"name":"Test name Three",
        "message":"Hello, it is my second message"}
        ).execute()

#  Update data to database
def update_data():
    supabase.table("room_one").update(
        {
        "message":"Hello, it is my second message"}
        ).eq("id", 3).execute()



#  Delete the data from database
def delete_data():
    supabase.table("room_one").delete().eq("id", 2).execute()
    
# delete the data from database old data
def delete_old_data():
    current_time = datetime.now()
    old_time = current_time - timedelta(minutes=2)
    formated_time = old_time.isoformat()
    
    supabase.table("room_one").delete().lt("created_at", formated_time).execute()
    
    

#  get to database
def select_data():
    data = supabase.table("room_one").select("*").execute()
    print(data)

# #  update post data to database 2 seconds after
# for i in range(15):
#     insert_data()
#     time.sleep(2)
    
    

# delete_old_data()
select_data()