from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings

client: AsyncIOMotorClient = None

async def connect_db():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URI)
    print("✅ MongoDB connected")

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    if client is None:
        raise Exception("Database not connected!")
    return client["smart_doctor_db"]