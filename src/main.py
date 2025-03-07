from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """lifespan it used to do task on specific time (startup, shotdoun)"""
    # Startup - get mango db connecton
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    try:
        yield
    finally:
        # Shutdown the connection
        app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)


# list of avaliable routes (you can find them in routes folder)
app.include_router(base.base_router)
app.include_router(data.data_router)
