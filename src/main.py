from fastapi import FastAPI
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser




app = FastAPI()

async def startup_span():
    # Startup - get mango db connecton
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # create object from the factory of llm and vectordb (act like routing class)
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    # Create generation client using defined model in settings (.env file)
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # Create embedding client using defined model in settings (.env file)
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)


    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    app.vectordb_client.connect()

    # intiatiate the language of rag
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

async def shutdown_span():
    # Shutdown the connection
    app.mongo_conn.close()
    app.vectordb_client.disconnect()

# lifespan it used to do task on specific time (startup, shotdoun)
#app.router.lifespan.on_startup.append(startup_span)
#app.router.lifespan.on_shutdown.append(shutdown_span)
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

# list of avaliable routes (you can find them in routes folder)
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
