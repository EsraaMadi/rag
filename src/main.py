from fastapi import FastAPI
from routes import base, data

app = FastAPI()

# list of avaliable routes (you can find them in routes folder)
app.include_router(base.base_router)
app.include_router(data.data_router)
