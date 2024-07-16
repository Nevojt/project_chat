
import secrets
import string

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import pytz
from sqlalchemy import select
from app.models import user_model, room_model, company_model
from app.config.utils import generate_random_code

# scheduler = AsyncIOScheduler()
def setup_scheduler(db_session_factory):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_old_rooms, 'cron', day='*', hour='0', args=[db_session_factory])
    scheduler.add_job(delete_test_users, 'cron', day='*', hour='0', args=[db_session_factory])
    scheduler.add_job(update_access_token, 'interval', hours=4, args=[db_session_factory])
    # scheduler.add_job(update_access_token, 'interval', minutes=1, args=[db_session_factory]) # test functionality

    scheduler.start()
    return scheduler


async def delete_old_rooms(db_session_factory):
    async with db_session_factory() as db:
        thirty_days_ago = datetime.now(pytz.utc) - timedelta(days=30)
        query = select(room_model.Rooms).where(room_model.Rooms.delete_at < thirty_days_ago)
        result = await db.execute(query)
        old_rooms = result.scalars().all()
        for room in old_rooms:
            await db.delete(room)
        await db.commit()
        
        
async def delete_test_users(db_session_factory):
    async with db_session_factory() as db:
        
        email_pattern = '%.testuser'
        
        query = select(user_model.User).where(user_model.User.email.like(email_pattern))
        result = await db.execute(query)
        test_users = result.scalars().all()
        for user in test_users:
            await db.delete(user)
        await db.commit()
        
async def update_access_token(db_session_factory):
    async with db_session_factory() as db:
        token_query = select(company_model.Company)
        result = await db.execute(token_query)
        companies = result.scalars().all()

        # Generate new access token
        for company in companies:
            company.code_verification = generate_random_code()
            db.add(company)
        await db.commit()

    
