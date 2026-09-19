import asyncio
from database import AsyncSessionLocal
from models import User
from sqlalchemy.future import select
from agents.spend_profiler import SpendProfiler
from dotenv import load_dotenv
import uuid

load_dotenv()

async def test():
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User))).scalars().first()
        if not user:
            print("No user found")
            return
        print(f"Testing for user: {user.id}")
        
        profiler = SpendProfiler(db_session=session, user_id=str(user.id))
        async for chunk in profiler.build_profile_stream():
            print(chunk)

if __name__ == "__main__":
    asyncio.run(test())
