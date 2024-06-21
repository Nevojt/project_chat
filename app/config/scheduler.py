from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from sqlalchemy import select
from app.database.async_db import async_session_maker
from app.models import models

def setup_scheduler(db_session_factory):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_old_rooms, 'cron', day='*', hour='0', args=[db_session_factory])
    # scheduler.add_job(
    #     delete_old_rooms,
    #     trigger=CronTrigger(minute='0'),  # Start awery day
    #     args=[db_session_factory]
    # )
    scheduler.start()
    return scheduler

async def delete_old_rooms(db_session_factory):
    async with db_session_factory() as db:
        thirty_days_ago = datetime.now(pytz.utc) - timedelta(days=30)
        query = select(models.Rooms).where(models.Rooms.delete_at < thirty_days_ago)
        result = await db.execute(query)
        old_rooms = result.scalars().all()
        for room in old_rooms:
            await db.delete(room)
        await db.commit()