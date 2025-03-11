from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory




app = FastAPI()

async def startup_db_client():
    # Startup - get mango db connecton
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # create object from the factory of llm (act like routing class)
    llm_provider_factory = LLMProviderFactory(settings)

    # Create generation client using defined model in settings (.env file)
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # Create embedding client using defined model in settings (.env file)
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

async def shutdown_db_client():
    # Shutdown the connection
    app.mongo_conn.close()

# lifespan it used to do task on specific time (startup, shotdoun)
app.router.lifespan.on_startup.append(startup_db_client)
app.router.lifespan.on_shutdown.append(shutdown_db_client)

# list of avaliable routes (you can find them in routes folder)
app.include_router(base.base_router)
app.include_router(data.data_router)

